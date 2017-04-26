from abc import abstractmethod, ABCMeta
from typing import Tuple, Union, Any, Optional, Iterable, Sequence, Generic, TypeVar

import collections

from hgicommon.models import Model

from sequencescape.enums import Property
from sequencescape.models import Study, NamedModel, InternalIdModel, AccessionNumberModel, Sample

MappedType = TypeVar("MappedType", bound=Model)


class Mapper(Generic[MappedType], metaclass=ABCMeta):
    """
    A data mapper as defined by Martin Fowler (see: http://martinfowler.com/eaaCatalog/dataMapper.html) that moves data
    between objects and a Sequencescape database, while keeping them independent of each other and the mapper itself.
    """
    @abstractmethod
    def add(self, model: Union[MappedType, Iterable[MappedType]]):
        """
        Adds data in the given model (of the type this data mapper deals with) to the database.
        :param model: the model containing that data to be transferred
        """

    @abstractmethod
    def get_all(self) -> Sequence[MappedType]:
        """
        Gets all the data of the type this data mapper deals with in the Sequencescape database.
        :return: a sequence of models representing each piece of data in the database of the type this data mapper
        deals with
        """

    @abstractmethod
    def _get_by_property_value_sequence(self, property: str, values: Iterable[Any]) -> Sequence[MappedType]:
        """
        Gets models (of the type this data mapper deals with) of data from the database that have one of the given
        values as the value of the given property.
        :param property: the property to match values to
        :param values: the values of the property to match
        :return: sequence of models that have at least one property value defined in the given acceptable values
        """

    def get_by_property_value(self, property: Union[str, Union[Tuple[str, Any]], Iterable[Tuple[str, Any]]],
                              values: Optional[Union[Any, Iterable[Any]]]=None) -> Sequence[MappedType]:
        """
        Gets models (of the type this data mapper deals with) of data from the database that have the given property
        values.
        :param property: TODO
        :param values: TODO
        :return: TODO
        """
        if isinstance(property, str):
            if isinstance(values, str) or isinstance(values, int):
                values = [values]
            return self._get_by_property_value_sequence(property, values)
        else:
            return self._get_by_property_value_tuple(property)

    def _get_by_property_value_tuple(
            self, property_value_tuples: Union[Tuple[str, Any], Iterable[Tuple[str, Any]]]) -> Sequence[MappedType]:
        """
        Gets models (of the type this data mapper deals with) of data from the database that have have one of the
        property values defined in a tuple from the given iterable.
        :param property_value_tuples: the tuples declaring what property values to match
        :return: sequence of models that have at least one property value defined in the given tuple iterable
        """
        if isinstance(property_value_tuples, tuple):
            property_value_tuples = [property_value_tuples]

        # TODO: Be clever and group tuples querying same property

        results = []
        for property, value in property_value_tuples:
            result = self.get_by_property_value(property, value)
            assert isinstance(result, collections.Sequence)
            results.extend(result)
        return results


class NamedMapper(Mapper[NamedModel], metaclass=ABCMeta):
    """
    Mapper for `Named` models.
    """
    def get_by_name(self, names: Union[str, Iterable[str]]) -> Sequence[NamedModel]:
        """
        Gets models (of the type this data mapper deals with) of data from the database that have the given names(s).
        :param names: the names or iterable of names of the data to get models for
        :return: sequence of models of data with the given names(s)
        """
        results = self.get_by_property_value(Property.NAME, names)
        assert isinstance(results, collections.Sequence)
        return results


class InternalIdMapper(Mapper[InternalIdModel], metaclass=ABCMeta):
    """
    Mapper for `InternalId` models.
    """
    def get_by_id(self, internal_ids: Union[int, Iterable[int]]) -> Union[Model, Sequence[InternalIdModel]]:
        """
        Gets models (of the type this data mapper deals with) of data from the database that have the given target(s).

        The property values this method uses are unique to each entry. Therefore, invoking this method with a single ID
        can return at most one model. For consistency, this return will be a sequence even if a single ID is used.
        :param internal_ids: the ids or iterable of ids of the data to get models for
        :return: sequence of models of data with the given target(s)
        """
        results = self.get_by_property_value(Property.INTERNAL_ID, internal_ids)
        assert isinstance(results, collections.Sequence)
        return results


class AccessionNumberMapper(Mapper[AccessionNumberModel], metaclass=ABCMeta):
    """
    Mapper for `AccessionNumber` models.
    """
    def get_by_accession_number(self, accession_numbers: Union[str, Iterable[str]]) -> Sequence[AccessionNumberModel]:
        """
        Gets models (of the type this data mapper deals with) of data from the database that have the given accession
        number(s).
        :param accession_numbers: the accession number or iterable of accession numbers of the data to get models for
        :return: sequence of models of data with the given accession number(s)
        """
        results = self.get_by_property_value(Property.ACCESSION_NUMBER, accession_numbers)
        assert isinstance(results, collections.Sequence)
        return results


class SampleMapper(NamedMapper, InternalIdMapper, AccessionNumberMapper, metaclass=ABCMeta):
    """
    Mapper for `Sample` models.
    """
    @abstractmethod
    def set_association_with_study(self, samples: Union[Sample, Iterable[Sample]], study: Study):
        """
        Associates the given samples to the given study.
        :param samples: the samples to associate to the study
        :param study: the study to which the samples are associated
        """

    @abstractmethod
    def get_associated_with_study(self, studies: Union[Study, Iterable[Study]]) -> Sequence[Sample]:
        """
        Gets all the samples that are associated to the given study or studies.
        :param studies: the studies to find associated samples for
        :return: samples that belong to one or more of the given studies
        """


class StudyMapper(NamedMapper, InternalIdMapper, AccessionNumberMapper, metaclass=ABCMeta):
    """
    Mapper for `Study` models.
    """
    @abstractmethod
    def set_association_with_sample(self, studies: Union[Study, Iterable[Study]], sample: Sample):
        """
        Associates the given studies to the given sample.
        :param studies: the studies to associate to the sample
        :param sample: the sample to which the studies are associated
        """

    @abstractmethod
    def get_associated_with_sample(self, samples: Union[Sample, Iterable[Sample]]) -> Sequence[Study]:
        """
        Gets all the studies that the given samples (identified by ID) belong to.
        :param samples: the samples that studies are to be got for
        :return: studies related to one or more of the given samples
        """


class LibraryMapper(NamedMapper, InternalIdMapper, metaclass=ABCMeta):
    """
    Mapper for `Library` models.
    """


class MultiplexedLibraryMapper(NamedMapper, InternalIdMapper, metaclass=ABCMeta):
    """
    Mapper for `MultiplexedLibrary` models.
    """


class WellMapper(NamedMapper, InternalIdMapper, metaclass=ABCMeta):
    """
    Mapper for `Well` models.
    """
