from hgijson import JsonPropertyMapping, MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
from sequencescape.models import Sample, InternalIdModel, NamedModel, Study, AccessionNumberModel, Library, Well, \
    MultiplexedLibrary

JSON_NAME_PROPERTY = "name"

JSON_INTERNAL_ID_PROPERTY = "internal_id"

JSON_ACCESSION_NUMBER_PROPERTY = "accession_number"

JSON_ORGANISM_PROPERTY = "organism"
JSON_COMMON_NAME_PROPERTY = "common_name"
JSON_TAXON_ID_PROPERTY = "taxon_id"
JSON_GENDER_PROPERTY = "gender"
JSON_ETHNICITY_PROPERTY = "ethnicity"
JSON_COHORT_PROPERTY = "cohort"
JSON_COUNTRY_OF_ORIGIN_PROPERTY = "country_of_origin"
JSON_GEOGRAPHICAL_REGION_PROPERTY = "geographical_region"

JSON_STUDY_TYPE = "type"
JSON_DESCRIPTION = "description"
JSON_STUDY_TITLE = "title"
JSON_STUDY_VISIBILITY = "visibility"
JSON_FACULTY_SPONSER = "faculty_sponsor"

JSON_LIBRARY_TYPE = "type"


# JSON encoder/decoder for `NamedModel`
_named_json_mapping = [
    JsonPropertyMapping(JSON_NAME_PROPERTY, "name")
]
_NamedModelJSONEncoder = MappingJSONEncoderClassBuilder(NamedModel, _named_json_mapping).build()
_NamedModelJSONDecoder = MappingJSONDecoderClassBuilder(NamedModel, _named_json_mapping).build()


# JSON encoder/decoder for `InternalIdModel`
_internal_id_json_mapping = [
    JsonPropertyMapping(JSON_INTERNAL_ID_PROPERTY, "internal_id")
]
_InternalIdModelJSONEncoder = MappingJSONEncoderClassBuilder(InternalIdModel, _internal_id_json_mapping).build()
_InternalIdModelJSONDecoder = MappingJSONDecoderClassBuilder(InternalIdModel, _internal_id_json_mapping).build()


# JSON encoder/decoder for `AccessionNumberModel`
_accession_number_json_mapping = [
    JsonPropertyMapping(JSON_ACCESSION_NUMBER_PROPERTY, "accession_number")
]
_AccessionNumberModelJSONEncoder = MappingJSONEncoderClassBuilder(AccessionNumberModel, _accession_number_json_mapping).build()
_AccessionNumberModelJSONDecoder = MappingJSONDecoderClassBuilder(AccessionNumberModel, _accession_number_json_mapping).build()


# JSON encoder/decoder for `Sample`
_sample_json_mapping = [
    JsonPropertyMapping(JSON_ORGANISM_PROPERTY, "organism"),
    JsonPropertyMapping(JSON_COMMON_NAME_PROPERTY, "common_name"),
    JsonPropertyMapping(JSON_TAXON_ID_PROPERTY, "taxon_id"),
    JsonPropertyMapping(JSON_GENDER_PROPERTY, "gender"),
    JsonPropertyMapping(JSON_ETHNICITY_PROPERTY, "ethnicity"),
    JsonPropertyMapping(JSON_COHORT_PROPERTY, "cohort"),
    JsonPropertyMapping(JSON_COUNTRY_OF_ORIGIN_PROPERTY, "country_of_origin"),
    JsonPropertyMapping(JSON_GEOGRAPHICAL_REGION_PROPERTY, "geographical_region")
]
SampleJSONEncoder = MappingJSONEncoderClassBuilder(
    Sample, _sample_json_mapping,
    (_NamedModelJSONEncoder, _AccessionNumberModelJSONEncoder, _InternalIdModelJSONEncoder)
).build()
SampleJSONDecoder = MappingJSONDecoderClassBuilder(
    Sample, _sample_json_mapping,
    (_NamedModelJSONDecoder, _AccessionNumberModelJSONDecoder, _InternalIdModelJSONDecoder)
).build()


# JSON encoder/decoder for `Study`
_study_json_mapping = [
    JsonPropertyMapping(JSON_STUDY_TYPE, "study_type"),
    JsonPropertyMapping(JSON_DESCRIPTION, "description"),
    JsonPropertyMapping(JSON_STUDY_TITLE, "study_title"),
    JsonPropertyMapping(JSON_STUDY_VISIBILITY, "study_visibility"),
    JsonPropertyMapping(JSON_FACULTY_SPONSER, "faculty_sponsor")
]
StudyJSONEncoder = MappingJSONEncoderClassBuilder(
    Study, _study_json_mapping, (_NamedModelJSONEncoder, _AccessionNumberModelJSONEncoder, _InternalIdModelJSONEncoder)
).build()
StudyJSONDecoder = MappingJSONDecoderClassBuilder(
    Study, _study_json_mapping, (_NamedModelJSONDecoder, _AccessionNumberModelJSONDecoder, _InternalIdModelJSONDecoder)
).build()


# JSON encoder/decoder for `Library`
_library_json_mapping = [
    JsonPropertyMapping(JSON_LIBRARY_TYPE, "library_type")
]
LibraryJSONEncoder = MappingJSONEncoderClassBuilder(
    Library, _library_json_mapping, (_NamedModelJSONEncoder, _InternalIdModelJSONEncoder)
).build()
LibraryJSONDecoder = MappingJSONDecoderClassBuilder(
    Library, _library_json_mapping, (_NamedModelJSONDecoder, _InternalIdModelJSONDecoder)
).build()


# JSON encoder/decoder for `MultiplexedLibrary`
_multiplexd_library_json_mapping = []
MultiplexedLibraryJSONEncoder = MappingJSONEncoderClassBuilder(
    MultiplexedLibrary, _multiplexd_library_json_mapping, (_NamedModelJSONEncoder, _InternalIdModelJSONEncoder)
).build()
MultiplexedLibraryJSONDecoder = MappingJSONDecoderClassBuilder(
    MultiplexedLibrary, _multiplexd_library_json_mapping, (_NamedModelJSONDecoder, _InternalIdModelJSONDecoder)
).build()


# JSON encoder/decoder for `Well`
_well_json_mapping = []
WellJSONEncoder = MappingJSONEncoderClassBuilder(
    Well, _well_json_mapping, (_NamedModelJSONEncoder, _InternalIdModelJSONEncoder)
).build()
WellJSONDecoder = MappingJSONDecoderClassBuilder(
    Well, _well_json_mapping, (_NamedModelJSONDecoder, _InternalIdModelJSONDecoder)
).build()
