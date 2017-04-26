from abc import ABCMeta

from hgicommon.models import Model

Model = Model

class NamedModel(Model, metaclass=ABCMeta):
    """
    Model that has a name.
    """
    def __init__(self, name: str=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name


class InternalIdModel(Model, metaclass=ABCMeta):
    """
    Model that has an internal ID.
    """
    def __init__(self, internal_id: int=None, **kwargs):
        super().__init__(**kwargs)
        self.internal_id = internal_id

    def __hash__(self) -> hash:
        return hash(self.internal_id)


class AccessionNumberModel(Model, metaclass=ABCMeta):
    """
    Model that has an accession number.
    """
    def __init__(self, accession_number: str=None, **kwargs):
        super().__init__(**kwargs)
        self.accession_number = accession_number


class Sample(NamedModel, InternalIdModel, AccessionNumberModel):
    """
    Model of a sample.
    """
    def __init__(self, organism: str=None, common_name: str=None, taxon_id: str=None, gender: str=None,
                 ethnicity: str=None, cohort: str=None, country_of_origin: str=None, geographical_region: str=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.organism = organism
        self.common_name = common_name
        self.taxon_id = taxon_id
        self.gender = gender
        self.ethnicity = ethnicity
        self.cohort = cohort
        self.country_of_origin = country_of_origin
        self.geographical_region = geographical_region


class Study(NamedModel, InternalIdModel, AccessionNumberModel):
    """
    Model of a study.
    """
    def __init__(self, study_type: str=None, description: str=None, study_title: str=None, study_visibility: str=None,
                 faculty_sponsor: str=None, **kwargs):
        super().__init__(**kwargs)
        self.study_type = study_type
        self.description = description
        self.study_title = study_title
        self.study_visibility = study_visibility
        self.faculty_sponsor = faculty_sponsor


class Library(NamedModel, InternalIdModel):
    """
    Model of a library.
    """
    def __init__(self, library_type: str=None, **kwargs):
        super().__init__(**kwargs)
        self.library_type = library_type


class MultiplexedLibrary(NamedModel, InternalIdModel):
    """
    Model of a multiplexed library.
    """


class Well(NamedModel, InternalIdModel):
    """
    Model of a well.
    """
