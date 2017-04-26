from typing import Union, Any, List, Tuple
from unittest.mock import MagicMock

from sequencescape.enums import Property
from sequencescape.mappers import Mapper, NamedMapper, InternalIdMapper, AccessionNumberMapper, SampleMapper,\
    WellMapper, MultiplexedLibraryMapper, LibraryMapper, StudyMapper
from sequencescape.models import Model, NamedModel, InternalIdModel, AccessionNumberModel


class MockMapper(Mapper):
    def __init__(self):
        self.add = MagicMock()
        self.get_all = MagicMock(return_value=[])
        self._get_by_property_value_sequence = MagicMock(return_value=[])
        self._get_by_property_value_tuple = MagicMock(return_value=[])

    def get_all(self) -> List[Model]:
        pass

    def add(self, model: Union[Model, List[Model]]):
        pass

    def _get_by_property_value_sequence(self, property: Property, values: Union[Any, List[Any]]) -> List[Model]:
        pass

    def _get_by_property_value_tuple(
            self, property_value_tuples: Union[Tuple[Property, Any], List[Tuple[Property, Any]]]) -> List[Model]:
        pass


class MockNamedMapper(MockMapper, NamedMapper):
    pass


class MockInternalIdMapper(MockMapper, InternalIdMapper):
    pass


class MockAccessionNumberMapper(MockMapper, AccessionNumberMapper):
    pass


class MockSampleMapper(MockMapper, SampleMapper):
    pass


class MockStudyMapper(MockMapper, StudyMapper):
    pass


class MockLibraryMapper(MockMapper, LibraryMapper):
    pass


class MockMultiplexedLibraryMapper(MockMapper, MultiplexedLibraryMapper):
    pass


class MockWellMapper(MockMapper, WellMapper):
    pass


class MockNamedModel(NamedModel):
    pass


class MockAccessionNumberModel(AccessionNumberModel):
    pass


class MockInternalIdModel(InternalIdModel):
    pass
