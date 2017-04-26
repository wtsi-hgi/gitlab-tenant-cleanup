import unittest

from typing import List

from sequencescape import NamedModel
from sequencescape.models import Sample, Study, Library, Well, MultiplexedLibrary
from sequencescape._sqlalchemy._models import SQLAlchemySample, SQLAlchemyStudy, SQLAlchemyLibrary, \
    SQLAlchemyWell, SQLAlchemyMultiplexedLibrary
from sequencescape._sqlalchemy.model_converters import get_equivalent_popo_model_type, \
    get_equivalent_sqlalchemy_model_type, convert_to_sqlalchemy_model, convert_to_popo_model, \
    convert_to_sqlalchemy_models, convert_to_popo_models
from sequencescape.tests._helpers import create_stub_sample, INTERNAL_ID, NAME, ACCESSION_NUMBER, ORGANISM,\
    COMMON_NAME, TAXON_ID, GENDER, ETHNICITY, COHORT, COUNTRY_OF_ORIGIN, GEOGRAPHICAL_REGION, create_stub_study, \
    STUDY_TYPE, DESCRIPTION, STUDY_TITLE, STUDY_VISIBILITY, FACULTY_SPONSOR, create_stub_library, LIBRARY_TYPE, \
    create_stub_well, create_stub_multiplexed_library


class TestGetEquivalentPopoModelType(unittest.TestCase):
    """
    Unit testing for `get_equivalent_popo_model_type`.
    """
    def test_raises_with_unsupported_type(self):
        self.assertRaises(ValueError, get_equivalent_popo_model_type, str)

    def test_correct_with_sample(self):
        self.assertEqual(get_equivalent_popo_model_type(SQLAlchemySample), Sample)

    def test_correct_with_study(self):
        self.assertEqual(get_equivalent_popo_model_type(SQLAlchemyStudy), Study)

    def test_correct_with_library(self):
        self.assertEqual(get_equivalent_popo_model_type(SQLAlchemyLibrary), Library)

    def test_correct_with_well(self):
        self.assertEqual(get_equivalent_popo_model_type(SQLAlchemyWell), Well)

    def test_correct_with_multiplexed_library(self):
        self.assertEqual(get_equivalent_popo_model_type(SQLAlchemyMultiplexedLibrary), MultiplexedLibrary)


class TestGetEquivalentSqlalchemyModelType(unittest.TestCase):
    """
    Unit testing for `get_equivalent_sqlalchemy_model_type`.
    """
    def test_raises_with_unsupported_type(self):
        self.assertRaises(ValueError, get_equivalent_sqlalchemy_model_type, str)

    def test_correct_with_sample(self):
        self.assertEqual(get_equivalent_sqlalchemy_model_type(Sample), SQLAlchemySample)

    def test_correct_with_study(self):
        self.assertEqual(get_equivalent_sqlalchemy_model_type(Study), SQLAlchemyStudy)

    def test_correct_with_library(self):
        self.assertEqual(get_equivalent_sqlalchemy_model_type(Library), SQLAlchemyLibrary)

    def test_correct_with_well(self):
        self.assertEqual(get_equivalent_sqlalchemy_model_type(Well), SQLAlchemyWell)

    def test_correct_with_multiplexed_library(self):
        self.assertEqual(get_equivalent_sqlalchemy_model_type(MultiplexedLibrary), SQLAlchemyMultiplexedLibrary)


class TestConvertToSQLAlchemyModel(unittest.TestCase):
    """
    Unit testing for `convert_to_sqlalchemy_model`.
    """
    def test_convert_sample(self):
        model = create_stub_sample()
        converted_model = convert_to_sqlalchemy_model(model)  # type: SQLAlchemySample
        self.assertEqual(converted_model.__class__, SQLAlchemySample)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)
        self.assertEqual(converted_model.accession_number, ACCESSION_NUMBER)
        self.assertEqual(converted_model.organism, ORGANISM)
        self.assertEqual(converted_model.common_name, COMMON_NAME)
        self.assertEqual(converted_model.taxon_id, TAXON_ID)
        self.assertEqual(converted_model.gender, GENDER)
        self.assertEqual(converted_model.ethnicity, ETHNICITY)
        self.assertEqual(converted_model.cohort, COHORT)
        self.assertEqual(converted_model.country_of_origin, COUNTRY_OF_ORIGIN)
        self.assertEqual(converted_model.geographical_region, GEOGRAPHICAL_REGION)

    def test_convert_study(self):
        model = create_stub_study()
        converted_model = convert_to_sqlalchemy_model(model)  # type: SQLAlchemyStudy
        self.assertEqual(converted_model.__class__, SQLAlchemyStudy)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)
        self.assertEqual(converted_model.accession_number, ACCESSION_NUMBER)
        self.assertEqual(converted_model.study_type, STUDY_TYPE)
        self.assertEqual(converted_model.description, DESCRIPTION)
        self.assertEqual(converted_model.study_title, STUDY_TITLE)
        self.assertEqual(converted_model.study_visibility, STUDY_VISIBILITY)
        self.assertEqual(converted_model.faculty_sponsor, FACULTY_SPONSOR)

    def test_convert_library(self):
        model = create_stub_library()
        converted_model = convert_to_sqlalchemy_model(model)  # type: SQLAlchemyLibrary
        self.assertEqual(converted_model.__class__, SQLAlchemyLibrary)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)
        self.assertEqual(converted_model.library_type, LIBRARY_TYPE)

    def test_convert_well(self):
        model = create_stub_well()
        converted_model = convert_to_sqlalchemy_model(model)  # type: SQLAlchemyWell
        self.assertEqual(converted_model.__class__, SQLAlchemyWell)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)

    def test_convert_multiplexed_library(self):
        model = create_stub_multiplexed_library()
        converted_model = convert_to_sqlalchemy_model(model)  # type: SQLAlchemyMultiplexedLibrary
        self.assertEqual(converted_model.__class__, SQLAlchemyMultiplexedLibrary)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)


class TestConvertToSQLAlchemyModels(unittest.TestCase):
    """
    TODO
    """
    def test_convert_many_of_same_type(self):
        names = ["name_1", "name_2"]
        models = [Sample(name=names[0]), Sample(name=names[1])]
        converted = convert_to_sqlalchemy_models(models)
        self.assertEquals([x.name for x in converted], [x.name for x in models])

    def test_convert_many_of_different_type(self):
        names = ["name_1", "name_2"]
        models = [Sample(name=names[0]), Library(name=names[1])]
        converted = convert_to_sqlalchemy_models(models)
        self.assertEquals([x.name for x in converted], [x.name for x in models])
        self.assertIsInstance(converted[0], SQLAlchemySample)
        self.assertIsInstance(converted[1], SQLAlchemyLibrary)


class TestConvertToPOPOModels(unittest.TestCase):
    """
    Using testing for `convert_to_popo_models`.
    """
    def test_convert_many_of_same_type(self):
        names = ["name_1", "name_2"]
        models = [SQLAlchemySample(), SQLAlchemySample()]
        models[0].name = names[0]
        models[1].name = names[1]
        converted = convert_to_popo_models(models)     # type: List[NamedModel]
        self.assertEquals([x.name for x in converted], [x.name for x in models])

    def test_convert_many_of_different_type(self):
        names = ["name_1", "name_2"]
        models = [SQLAlchemySample(), SQLAlchemyLibrary()]
        models[0].name = names[0]
        models[1].name = names[1]
        converted = convert_to_popo_models(models)     # type: List[NamedModel]
        self.assertEquals([x.name for x in converted], [x.name for x in models])
        self.assertIsInstance(converted[0], Sample)
        self.assertIsInstance(converted[1], Library)


class TestConvertToPopoModel(unittest.TestCase):
    """
    Unit testing for `convert_to_popo_model`.
    """
    def test_convert_sample(self):
        alchemy_model = convert_to_sqlalchemy_model(create_stub_sample())
        converted_model = convert_to_popo_model(alchemy_model)  # type: Sample
        self.assertEqual(converted_model.__class__, Sample)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)
        self.assertEqual(converted_model.accession_number, ACCESSION_NUMBER)
        self.assertEqual(converted_model.organism, ORGANISM)
        self.assertEqual(converted_model.common_name, COMMON_NAME)
        self.assertEqual(converted_model.taxon_id, TAXON_ID)
        self.assertEqual(converted_model.gender, GENDER)
        self.assertEqual(converted_model.ethnicity, ETHNICITY)
        self.assertEqual(converted_model.cohort, COHORT)
        self.assertEqual(converted_model.country_of_origin, COUNTRY_OF_ORIGIN)
        self.assertEqual(converted_model.geographical_region, GEOGRAPHICAL_REGION)

    def test_convert_study(self):
        alchemy_model = convert_to_sqlalchemy_model(create_stub_study())
        converted_model = convert_to_popo_model(alchemy_model)  # type: Study
        self.assertEqual(converted_model.__class__, Study)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)
        self.assertEqual(converted_model.accession_number, ACCESSION_NUMBER)
        self.assertEqual(converted_model.study_type, STUDY_TYPE)
        self.assertEqual(converted_model.description, DESCRIPTION)
        self.assertEqual(converted_model.study_title, STUDY_TITLE)
        self.assertEqual(converted_model.study_visibility, STUDY_VISIBILITY)
        self.assertEqual(converted_model.faculty_sponsor, FACULTY_SPONSOR)

    def test_convert_library(self):
        alchemy_model = convert_to_sqlalchemy_model(create_stub_library())
        converted_model = convert_to_popo_model(alchemy_model)  # type: Library
        self.assertEqual(converted_model.__class__, Library)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)
        self.assertEqual(converted_model.library_type, LIBRARY_TYPE)

    def test_convert_well(self):
        alchemy_model = convert_to_sqlalchemy_model(create_stub_well())
        converted_model = convert_to_popo_model(alchemy_model)  # type: Well
        self.assertEqual(converted_model.__class__, Well)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)

    def test_convert_multiplexed_library(self):
        alchemy_model = convert_to_sqlalchemy_model(create_stub_multiplexed_library())
        converted_model = convert_to_popo_model(alchemy_model)  # type: MultiplexedLibrary
        self.assertEqual(converted_model.__class__, MultiplexedLibrary)
        self.assertEqual(converted_model.internal_id, INTERNAL_ID)
        self.assertEqual(converted_model.name, NAME)


if __name__ == "__main__":
    unittest.main()
