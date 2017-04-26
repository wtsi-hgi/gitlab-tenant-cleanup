import collections
from abc import ABCMeta
from typing import Union, Any, Iterable, Sequence, TypeVar

from sqlalchemy import Column

from hgicommon.models import Model
from sequencescape._sqlalchemy.database_connector import SQLAlchemyDatabaseConnector
from sequencescape._sqlalchemy.model_converters import convert_to_sqlalchemy_model, convert_to_popo_models,\
    get_equivalent_sqlalchemy_model_type, convert_to_sqlalchemy_models
from sequencescape.enums import Property
from sequencescape.mappers import Mapper, LibraryMapper, MultiplexedLibraryMapper, SampleMapper, WellMapper, StudyMapper, \
    MappedType
from sequencescape.models import Library, MultiplexedLibrary, Sample, Well, Study, InternalIdModel

_InternalIdMappedType = TypeVar("InternalIdMappedType", bound=InternalIdModel)


class SQLAlchemyMapper(Mapper[MappedType], metaclass=ABCMeta):
    """
    Implementation of `Mapper` using SQLAlchemy.
    """
    def __init__(self, database_connector: SQLAlchemyDatabaseConnector, model_type: type):
        """
        Constructor.
        :param database_connector: the object through which database connections can be made
        :param model_type: the type of the model that the metadata_mapper is used for. Note that it is not (currently)
        possible in Python to get this type from the generic used
        """
        if not model_type:
            raise ValueError("Model type must be specified through `model_type` parameter")
        if not issubclass(model_type, Model):
            raise ValueError("Model type (%s) must be a subclass of `Model`" % model_type)

        self._database_connector = database_connector
        self._model_type = model_type
        self._sqlalchemy_model_type = get_equivalent_sqlalchemy_model_type(self._model_type)

        if self._sqlalchemy_model_type is None:
            raise NotImplementedError("Not implemented for models of type: `%s`" % model_type)

    def add(self, models: Union[Model, Iterable[MappedType]]):
        if models is None:
            raise ValueError("Cannot add `None`")
        if not isinstance(models, list):
            models = [models]

        session = self._database_connector.create_session()
        for model in models:
            sqlalchemy_model = convert_to_sqlalchemy_model(model)
            session.add(sqlalchemy_model)
        session.commit()
        session.close()

    def get_all(self) -> Sequence[MappedType]:
        query_model = self._sqlalchemy_model_type
        session = self._database_connector.create_session()
        result = session.query(query_model).all()
        session.close()
        assert isinstance(result, collections.Sequence)
        return convert_to_popo_models(result)

    def _get_by_property_value_sequence(self, property: Property, required_property_values: Iterable[Any]) \
            -> Sequence[MappedType]:
        query_model = self._sqlalchemy_model_type
        session = self._database_connector.create_session()

        # FIXME: It is an assumption that the Model property has the same name as SQLAlchemyModel property
        query_column = query_model.__dict__[property]   # type: Column
        results = session.query(query_model). \
            filter(query_column.in_(required_property_values)).\
            all()
        session.close()
        assert isinstance(results, collections.Sequence)
        return convert_to_popo_models(results)


class SQLAssociationMapper(SQLAlchemyMapper[_InternalIdMappedType], metaclass=ABCMeta):
    """
    SQLAlchemy metadata_mapper that deals with models that can be associated with other models via a join table.
    """
    def _set_association(self, associate: Union[InternalIdModel, Iterable[InternalIdModel]],
                         associate_with: InternalIdModel, relationship_property_name: str):
        """
        Associates the given models to another model, linked to via the specified relationship property.
        :param associate: the models to associate
        :param associate_with: the model to associate with
        :param relationship_property_name: the property on `associate_with` in which the relationship is expressed
        """
        if associate_with.internal_id is None:
            raise ValueError("Model to associate with must have an internal ID: %s" % associate_with)

        if isinstance(associate, InternalIdModel):
            associate = [associate]

        session = self._database_connector.create_session()
        sqlalchemy_associated_with_type = get_equivalent_sqlalchemy_model_type(associate_with.__class__)
        assert sqlalchemy_associated_with_type is not None

        # sqlalchemy_associated_with_type = SQLAlchemyStudy
        results = session.query(sqlalchemy_associated_with_type). \
            filter(sqlalchemy_associated_with_type.internal_id == associate_with.internal_id).all()

        if len(results) != 1:
            raise ValueError("Model to associate with does not exist:\n%s" % associate_with)

        # FIXME: SQLAlchemy wants to insert the `associate` records. Could not find out how to stop this so hacking by
        #        deleting from the database. If the given model is not in sync with the  database this will lead to data
        #        loss.
        sqlalchemy_associate_type = get_equivalent_sqlalchemy_model_type(associate[0].__class__)
        assert sqlalchemy_associate_type is not None
        for associate_element in associate:
            session.query(sqlalchemy_associate_type).\
                filter(sqlalchemy_associate_type.internal_id == associate_element.internal_id).\
                delete()

        sqlalchemy_associate = convert_to_sqlalchemy_models(associate)
        for result in results:
            for sqlalchemy_associate_element in sqlalchemy_associate:
                current_relationship = getattr(result, relationship_property_name)
                if sqlalchemy_associate_element not in current_relationship:
                    setattr(result, relationship_property_name, current_relationship + sqlalchemy_associate)

        session.commit()
        session.close()

    def _get_association(self, associated_with: Union[InternalIdModel, Iterable[InternalIdModel]],
                         relationship_property_name: str) -> Sequence[_InternalIdMappedType]:
        """
        Gets the models that are associated to another model, linked to via the specified relationship property.
        :param associated_with: the model to find other models that are associated with it
        :param relationship_property_name: the property on `associated_with` in which the relationship is expressed
        :return: all models associated with the given `associated_with` model
        """
        if isinstance(associated_with, InternalIdModel):
            associated_with = [associated_with]
        if len(associated_with) == 0:
            return []

        session = self._database_connector.create_session()
        sqlalchemy_associated_with_type = get_equivalent_sqlalchemy_model_type(associated_with[0].__class__)
        assert sqlalchemy_associated_with_type is not None
        results = session.query(sqlalchemy_associated_with_type). \
            filter(sqlalchemy_associated_with_type.internal_id.
            in_([x.internal_id for x in associated_with])). \
            all()
        assert isinstance(results, collections.Sequence)

        if len(results) != len(associated_with):
            raise ValueError(
                "Not all given models to find associations with exist in the database.\nGiven: %s\nExisting: %s"
                % (associated_with, convert_to_popo_models(results)))

        associated = []
        for result in results:
            relationships = getattr(result, relationship_property_name)
            if not isinstance(relationships, list):
                relationships = [relationships]
            # Ensure only gets put in `associated` list once, even if the associate is associated with many of the given
            # `associated_with` models.
            for relationship in relationships:
                if relationship not in associated:
                    associated.append(relationship)
        session.close()

        return convert_to_popo_models(associated)


class SQLAlchemySampleMapper(SQLAssociationMapper[MappedType], SampleMapper):
    """
    Implementation of `SampleMapper` using SQLAlchemy.
    """
    def __init__(self, database_connector: SQLAlchemyDatabaseConnector):
        """
        Constructor.
        :param database_connector: the database connector
        """
        super().__init__(database_connector, Sample)

    def set_association_with_study(self, samples: Union[Sample, Iterable[Sample]], study: Study):
        self._set_association(samples, study, "samples")

    def get_associated_with_study(self, studies: Union[Study, Iterable[Study]]) -> Sequence[Sample]:
        return self._get_association(studies, "samples")


class SQLAlchemyStudyMapper(SQLAssociationMapper[Study], StudyMapper):
    """
    Implementation of `StudyMapper` using SQLAlchemy.
    """
    def __init__(self, database_connector: SQLAlchemyDatabaseConnector):
        """
        Constructor.
        :param database_connector: the database connector
        """
        super().__init__(database_connector, Study)

    def set_association_with_sample(self, studies: Union[Study, Iterable[Study]], sample: Sample):
        self._set_association(studies, sample, "studies")

    def get_associated_with_sample(self, samples: Union[Sample, Iterable[Sample]]) -> Sequence[Study]:
        return self._get_association(samples, "studies")


class SQLAlchemyLibraryMapper(SQLAlchemyMapper[Library], LibraryMapper):
    """
    Implementation of `LibraryMapper` using SQLAlchemy.
    """
    def __init__(self, database_connector: SQLAlchemyDatabaseConnector):
        """
        Constructor.
        :param database_connector: the database connector
        """
        super().__init__(database_connector, Library)


class SQLAlchemyWellMapper(SQLAlchemyMapper[Well], WellMapper):
    """
    Implementation of `WellMapper` using SQLAlchemy.
    """
    def __init__(self, database_connector: SQLAlchemyDatabaseConnector):
        """
        Constructor.
        :param database_connector: the database connector
        """
        super().__init__(database_connector, Well)


class SQLAlchemyMultiplexedLibraryMapper(SQLAlchemyMapper[MultiplexedLibrary], MultiplexedLibraryMapper):
    """
    Implementation of `MultiplexedLibraryMapper` using SQLAlchemy.
    """
    def __init__(self, database_connector: SQLAlchemyDatabaseConnector):
        """
        Constructor.
        :param database_connector: the database connector
        """
        super().__init__(database_connector, MultiplexedLibrary)
