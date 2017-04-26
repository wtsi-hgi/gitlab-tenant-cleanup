from sequencescape import WellJSONDecoder, WellJSONEncoder
from sequencescape.json_converters import JSON_INTERNAL_ID_PROPERTY, MultiplexedLibraryJSONDecoder, \
    MultiplexedLibraryJSONEncoder, LibraryJSONDecoder, LibraryJSONEncoder, JSON_LIBRARY_TYPE, StudyJSONDecoder, \
    StudyJSONEncoder, JSON_FACULTY_SPONSER, JSON_STUDY_VISIBILITY, JSON_STUDY_TITLE, JSON_DESCRIPTION, JSON_STUDY_TYPE, \
    JSON_ACCESSION_NUMBER_PROPERTY, SampleJSONDecoder, SampleJSONEncoder, JSON_GEOGRAPHICAL_REGION_PROPERTY, \
    JSON_COUNTRY_OF_ORIGIN_PROPERTY, JSON_COHORT_PROPERTY, JSON_ETHNICITY_PROPERTY, JSON_GENDER_PROPERTY, \
    JSON_TAXON_ID_PROPERTY, JSON_COMMON_NAME_PROPERTY, JSON_ORGANISM_PROPERTY
from sequencescape.json_converters import JSON_NAME_PROPERTY
from sequencescape.tests._helpers import create_stub_well, create_stub_multiplexed_library, create_stub_library, \
    create_stub_study, create_stub_sample
from sequencescape.tests._json_converters_test_factory import create_json_converter_test


_setups = [(
        create_stub_sample,
        [JSON_NAME_PROPERTY, JSON_INTERNAL_ID_PROPERTY, JSON_ACCESSION_NUMBER_PROPERTY, JSON_ORGANISM_PROPERTY,
         JSON_COMMON_NAME_PROPERTY, JSON_TAXON_ID_PROPERTY, JSON_GENDER_PROPERTY, JSON_ETHNICITY_PROPERTY,
         JSON_COHORT_PROPERTY, JSON_COUNTRY_OF_ORIGIN_PROPERTY, JSON_GEOGRAPHICAL_REGION_PROPERTY],
        SampleJSONEncoder,
        SampleJSONDecoder
    ), (
        create_stub_study,
        [JSON_NAME_PROPERTY, JSON_INTERNAL_ID_PROPERTY, JSON_ACCESSION_NUMBER_PROPERTY, JSON_STUDY_TYPE, JSON_DESCRIPTION,
         JSON_STUDY_TITLE, JSON_STUDY_VISIBILITY, JSON_FACULTY_SPONSER],
        StudyJSONEncoder,
        StudyJSONDecoder
    ), (
        create_stub_library,
        [JSON_NAME_PROPERTY, JSON_INTERNAL_ID_PROPERTY, JSON_LIBRARY_TYPE],
        LibraryJSONEncoder,
        LibraryJSONDecoder
    ), (
        create_stub_multiplexed_library,
        [JSON_NAME_PROPERTY, JSON_INTERNAL_ID_PROPERTY],
        MultiplexedLibraryJSONEncoder,
        MultiplexedLibraryJSONDecoder
    ), (
        create_stub_well,
        [JSON_NAME_PROPERTY, JSON_INTERNAL_ID_PROPERTY],
        WellJSONEncoder,
        WellJSONDecoder
    )
]

for _setup in _setups:
    _encoder_test_class, _decoder_test_class = create_json_converter_test(*_setup)
    globals()[_encoder_test_class.__name__] = _encoder_test_class
    globals()[_decoder_test_class.__name__] = _decoder_test_class
    del _encoder_test_class, _decoder_test_class
