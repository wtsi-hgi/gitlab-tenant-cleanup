from typing import List

from sequencescape import InternalIdModel, Study, Sample, Library, MultiplexedLibrary, Well

INTERNAL_ID = 123
NAME = "NAME123"
ACCESSION_NUMBER = "ACCESSION_NUMBER123"

ORGANISM = "ORGANISM123"
COMMON_NAME = "COMMON_NAME123"
TAXON_ID = "TAXON_ID123"
GENDER = "GENDER123"
ETHNICITY = "ETHNICITY123"
COHORT = "COHORT123"
COUNTRY_OF_ORIGIN = "COUNTRY_OF_ORIGIN123"
GEOGRAPHICAL_REGION = "GEOGRAPHICAL_REGION123"

STUDY_TYPE = "STUDY_TYPE123"
DESCRIPTION = "DESCRIPTION123"
STUDY_TITLE = "STUDY_TITLE123"
STUDY_VISIBILITY = "STUDY_VISIBILITY123"
FACULTY_SPONSOR = "FACULTY_SPONSOR123"

LIBRARY_TYPE = "LIBRARY_TYPE123"


def assign_unique_ids(models: List[InternalIdModel]) -> List[InternalIdModel]:
    """
    Gives each model in the list a unique ID. IDs are deterministic, based on each model's position in the list.
    :param models: the models to give unique internal IDs to
    :return: the models
    """
    for i in range(len(models)):
        model = models[i]
        model.internal_id = i
    return models


def create_stub(model_type: type):
    """
    Creates a mock of an object of the given type
    :param model_type: the type of model object to create a mock of
    :return: the mock model object
    """
    mappings = {
        Sample: create_stub_sample,
        Study: create_stub_study,
        Library: create_stub_library,
        MultiplexedLibrary: create_stub_multiplexed_library,
        Well: create_stub_well
    }
    return mappings[model_type]()


def create_stub_sample() -> Sample:
    """
    Creates a `Sample` stub.
    :return: stub a `Sample` model
    """
    sample = Sample()
    sample.internal_id = INTERNAL_ID
    sample.name = NAME
    sample.accession_number = ACCESSION_NUMBER
    sample.organism = ORGANISM
    sample.common_name = COMMON_NAME
    sample.taxon_id = TAXON_ID
    sample.gender = GENDER
    sample.ethnicity = ETHNICITY
    sample.cohort = COHORT
    sample.country_of_origin = COUNTRY_OF_ORIGIN
    sample.geographical_region = GEOGRAPHICAL_REGION
    return sample


def create_stub_study() -> Study:
    """
    Creates a `Study` stub.
    :return: stub a `Study` model
    """
    study = Study()
    study.internal_id = INTERNAL_ID
    study.name = NAME
    study.accession_number = ACCESSION_NUMBER
    study.study_type = STUDY_TYPE
    study.description = DESCRIPTION
    study.study_title = STUDY_TITLE
    study.study_visibility = STUDY_VISIBILITY
    study.faculty_sponsor = FACULTY_SPONSOR
    return study


def create_stub_library() -> Library:
    """
    Creates a `Library` stub.
    :return: stub a `Library` model
    """
    library = Library()
    library.internal_id = INTERNAL_ID
    library.name = NAME
    library.library_type = LIBRARY_TYPE
    return library


def create_stub_multiplexed_library() -> MultiplexedLibrary:
    """
    Creates a `MultiplexedLibrary` stub.
    :return: stub a `MultiplexedLibrary` model
    """
    multiplexed_library = MultiplexedLibrary()
    multiplexed_library.internal_id = INTERNAL_ID
    multiplexed_library.name = NAME
    return multiplexed_library


def create_stub_well() -> Well:
    """
    Creates a `Well` stub.
    :return: stub a `Well` model
    """
    well = Well()
    well.internal_id = INTERNAL_ID
    well.name = NAME
    return well
