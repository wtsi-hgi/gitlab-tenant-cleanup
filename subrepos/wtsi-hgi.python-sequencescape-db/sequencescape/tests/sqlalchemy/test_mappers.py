import unittest
from abc import abstractmethod, ABCMeta
from typing import List

from sequencescape._sqlalchemy.database_connector import SQLAlchemyDatabaseConnector
from sequencescape._sqlalchemy.mappers import SQLAlchemyMapper, SQLAlchemySampleMapper, SQLAlchemyStudyMapper, \
    SQLAlchemyLibraryMapper, SQLAlchemyWellMapper, SQLAlchemyMultiplexedLibraryMapper
from sequencescape.enums import Property
from sequencescape.mappers import Mapper
from sequencescape.models import InternalIdModel, Sample, Study
from sequencescape.tests._helpers import create_stub_sample, assign_unique_ids, create_stub_study, create_stub_library, \
    create_stub_multiplexed_library, create_stub_well
from sequencescape.tests.sqlalchemy.stub_database import create_stub_database


def _create_connector() -> SQLAlchemyDatabaseConnector:
    """
    Creates a connector to a test database.
    :return: connector to a test database
    """
    database_location, dialect = create_stub_database()
    connector = SQLAlchemyDatabaseConnector("%s:///%s" % (dialect, database_location))
    return connector


class _SQLAlchemyMapperTest(unittest.TestCase, metaclass=ABCMeta):
    """
    Tests for `SQLAlchemyMapper`.
    """
    @staticmethod
    def _get_internal_ids(models: List[InternalIdModel]) -> List[int]:
        """
        Gets the ids of all of the given models.
        :param models: the models to get_by_path the ids of
        :return: the ids of the given models
        """
        return [model.internal_id for model in models]

    @abstractmethod
    def _create_model(self) -> InternalIdModel:
        """
        Creates a model of the type the mapper being tested uses.
        :return: model for use with SUT
        """

    @abstractmethod
    def _create_mapper(self, connector: SQLAlchemyDatabaseConnector) -> SQLAlchemyMapper:
        """
        Creates the mapper that is to be tested.
        :return: mapper to be tested
        """

    def setUp(self):
        self._connector = _create_connector()
        self._mapper = self._create_mapper(self._connector)

    def test_add_with_none(self):
        self.assertRaises(ValueError, self._mapper.add, None)

    def test_add_with_non_model(self):
        self.assertRaises(ValueError, self._mapper.add, Mapper)

    def test_add_with_empty_list(self):
        self._mapper.add([])

        retrieved_models = self._mapper.get_all()
        self.assertEqual(len(retrieved_models), 0)

    def test_add_with_model(self):
        model = self._create_models(1)[0]
        self._mapper.add(model)

        retrieved_models = self._mapper.get_all()
        self.assertEqual(len(retrieved_models), 1)
        self.assertEqual(retrieved_models[0], model)

    def test_add_with_model_list(self):
        models = self._create_models(5)
        self._mapper.add(models)

        retrieved_models = self._mapper.get_all()
        self.assertCountEqual(retrieved_models, models)

    def test__get_by_property_value_sequence_with_empty_list(self):
        models = self._create_models(5)
        models_to_retrieve = []
        self._mapper.add(models)

        retrieved_models = self._mapper._get_by_property_value_sequence(
            Property.INTERNAL_ID, self._get_internal_ids(models_to_retrieve))
        self.assertCountEqual(retrieved_models, models_to_retrieve)

    def test__get_by_property_value_sequence_with_list_of_existing(self):
        models = self._create_models(5)
        models_to_retrieve = [models[0], models[2]]
        self._mapper.add(models)

        retrieved_models = self._mapper._get_by_property_value_sequence(
            Property.INTERNAL_ID, self._get_internal_ids(models_to_retrieve))
        self.assertCountEqual(retrieved_models, models_to_retrieve)

    def test__get_by_property_value_sequence_with_list_of_non_existing(self):
        models = self._create_models(5)
        models_to_retrieve = [models.pop(), models.pop()]
        assert len(models) == 3
        self._mapper.add(models)

        retrieved_models = self._mapper._get_by_property_value_sequence(
            Property.INTERNAL_ID, self._get_internal_ids(models_to_retrieve))
        self.assertCountEqual(retrieved_models, [])

    def test__get_by_property_value_sequence_with_list_of_both_existing_and_non_existing(self):
        models = self._create_models(5)
        models_to_retrieve = [models[0], models[2], models.pop()]
        assert len(models) == 4
        self._mapper.add(models)

        retrieved_models = self._mapper._get_by_property_value_sequence(
            Property.INTERNAL_ID, self._get_internal_ids(models_to_retrieve))
        self.assertCountEqual(retrieved_models, models_to_retrieve[:2])

    def test__get_by_property_value_sequence_returns_correct_type(self):
        models = self._create_models(5)
        self._mapper.add(models)

        retrieved_models = self._mapper._get_by_property_value_sequence(
            Property.INTERNAL_ID, self._get_internal_ids(models))
        self.assertCountEqual(retrieved_models, models)
        self.assertIsInstance(retrieved_models[0], models[0].__class__)

    def _create_models(self, number_of_models: int) -> List[InternalIdModel]:
        """
        Creates a number of models to use in tests.
        :param number_of_models: the number of models to create
        :return: the models
        """
        return assign_unique_ids([self._create_model() for _ in range(number_of_models)])


class _SQLAssociationMapperTest(_SQLAlchemyMapperTest):
    """
    Tests for `SQLAssociationMapper`.
    """
    @abstractmethod
    def _get_associated_with_instance(self, internal_id=None) -> InternalIdModel:
        """
        Gets an instance of the type which the objects the mapper deals with can be associated to.
        :return: instance that the object that the mapper is for can be assocaited with
        """

    def setUp(self):
        super().setUp()
        self._associated_with_type = self._get_associated_with_instance().__class__.__name__
        self._associated_with_mapper = globals()["SQLAlchemy%sMapper" % self._associated_with_type](self._connector)
        self._mapper_get_associated_with_x = getattr(
            self._mapper, "get_associated_with_%s" % self._associated_with_type.lower())
        self._mapper_set_association_with_x = getattr(
            self._mapper, "set_association_with_%s" % self._associated_with_type.lower())

    def test__get_associated_with_x_with_non_existent_x(self):
        self.assertRaises(ValueError, self._mapper_get_associated_with_x, self._get_associated_with_instance())

    def test__get_associated_with_x_with_non_associated(self):
        x = self._get_associated_with_instance()
        self._associated_with_mapper.add(x)

        associated = self._mapper_get_associated_with_x(x)
        self.assertEquals(len(associated), 0)

    def test__get_associated_with_x_with_value(self):
        x = self._get_associated_with_instance()
        self._associated_with_mapper.add(x)

        models = self._create_models(2)
        self._mapper.add(models)
        self._mapper_set_association_with_x(models, x)

        associated = self._mapper_get_associated_with_x(x)
        self.assertCountEqual(associated, models)

    def test__get_associated_with_x_with_empty_list(self):
        self._mapper_get_associated_with_x([])

    def test__get_associated_with_x_with_list(self):
        models = self._create_models(2)
        self._mapper.add(models)

        xs = [self._get_associated_with_instance(i) for i in range(2)]
        self._associated_with_mapper.add(xs)

        self._mapper_set_association_with_x(models[0], xs[0])
        self._mapper_set_association_with_x(models[1], xs[1])

        associated = self._mapper_get_associated_with_x(xs)
        self.assertCountEqual(associated, models)

    def test__get_associated_with_x_with_list_and_shared_association(self):
        xs = [self._get_associated_with_instance(i) for i in range(2)]
        self._associated_with_mapper.add(xs)

        model = self._create_model()
        self._mapper.add(model)

        self._mapper_set_association_with_x(model, xs[0])
        self._mapper_set_association_with_x(model, xs[1])

        associated = self._mapper_get_associated_with_x(xs)
        self.assertCountEqual(associated, [model])


class SQLAlchemySampleMapperTest(_SQLAssociationMapperTest):
    """
    Tests for `SQLAlchemySampleMapper`.
    """
    def _create_model(self) -> InternalIdModel:
        return create_stub_sample()

    def _create_mapper(self, connector: SQLAlchemyDatabaseConnector) -> SQLAlchemyMapper:
        return SQLAlchemySampleMapper(connector)

    def _get_associated_with_instance(self, internal_id=None) -> InternalIdModel:
        study = create_stub_study()
        if internal_id is not None:
            study.internal_id = internal_id
        return study


class SQLAlchemyStudyMapperTest(_SQLAssociationMapperTest):
    """
    Tests for `SQLAlchemyStudyMapper`.
    """
    def _create_model(self) -> InternalIdModel:
        return create_stub_study()

    def _create_mapper(self, connector: SQLAlchemyDatabaseConnector) -> SQLAlchemyMapper:
        return SQLAlchemyStudyMapper(connector)

    def _get_associated_with_instance(self, internal_id=None) -> InternalIdModel:
        study = create_stub_sample()
        if internal_id is not None:
            study.internal_id = internal_id
        return study


class SQLAlchemyLibraryMapperTest(_SQLAlchemyMapperTest):
    """
    Tests for `SQLAlchemyLibraryMapper`.
    """
    def _create_model(self) -> InternalIdModel:
        return create_stub_library()

    def _create_mapper(self, connector: SQLAlchemyDatabaseConnector) -> SQLAlchemyMapper:
        return SQLAlchemyLibraryMapper(connector)


class SQLAlchemyWellMapperTest(_SQLAlchemyMapperTest):
    """
    Tests for `SQLAlchemyWellMapper`.
    """
    def _create_model(self) -> InternalIdModel:
        return create_stub_well()

    def _create_mapper(self, connector: SQLAlchemyDatabaseConnector) -> SQLAlchemyMapper:
        return SQLAlchemyWellMapper(connector)


class SQLAlchemyMultiplexedLibraryMapperTest(_SQLAlchemyMapperTest):
    """
    Tests for `SQLAlchemyMultiplexedLibraryMapper`.
    """
    def _create_model(self) -> InternalIdModel:
        return create_stub_multiplexed_library()

    def _create_mapper(self, connector: SQLAlchemyDatabaseConnector) -> SQLAlchemyMapper:
        return SQLAlchemyMultiplexedLibraryMapper(connector)


# Trick required to stop Python's unittest from running the abstract base classes as tests
del _SQLAlchemyMapperTest
del _SQLAssociationMapperTest


if __name__ == "__main__":
    unittest.main()
