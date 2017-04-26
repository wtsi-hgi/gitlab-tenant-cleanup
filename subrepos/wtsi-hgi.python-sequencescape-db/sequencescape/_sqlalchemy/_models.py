from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

SQLAlchemyModel = declarative_base()

study_sample_join_table = Table("current_study_samples", SQLAlchemyModel.metadata,
    Column("sample_internal_id", Integer, ForeignKey("current_samples.internal_id")),
    Column("study_internal_id", Integer, ForeignKey("current_studies.internal_id"))
)


class SQLAlchemyNamedModel(SQLAlchemyModel):
    __abstract__ = True
    name = Column(String)


class SQLAlchemyInternalIdModel(SQLAlchemyModel):
    __abstract__ = True
    internal_id = Column(Integer, primary_key=True)


class SQLAlchemyAccessionNumberModel(SQLAlchemyModel):
    __abstract__ = True
    accession_number = Column(String)


class SQLAlchemySample(SQLAlchemyNamedModel, SQLAlchemyInternalIdModel, SQLAlchemyAccessionNumberModel):
    __tablename__ = "current_samples"
    organism = Column(String)
    common_name = Column(String)
    taxon_id = Column(String)
    gender = Column(String)
    ethnicity = Column(String)
    cohort = Column(String)
    country_of_origin = Column(String)
    geographical_region = Column(String)
    studies = relationship("SQLAlchemyStudy", secondary=study_sample_join_table)


class SQLAlchemyStudy(SQLAlchemyNamedModel, SQLAlchemyInternalIdModel, SQLAlchemyAccessionNumberModel):
    __tablename__ = "current_studies"
    study_type = Column(String)
    description = Column(String)
    study_title = Column(String)
    study_visibility = Column(String)
    faculty_sponsor = Column(String)
    samples = relationship("SQLAlchemySample", secondary=study_sample_join_table)


class SQLAlchemyLibrary(SQLAlchemyNamedModel, SQLAlchemyInternalIdModel):
    __tablename__ = "current_library_tubes"
    library_type = Column(String)


class SQLAlchemyMultiplexedLibrary(SQLAlchemyNamedModel, SQLAlchemyInternalIdModel):
    __tablename__ = "current_multiplexed_library_tubes"


class SQLAlchemyWell(SQLAlchemyNamedModel, SQLAlchemyInternalIdModel):
    __tablename__ = "current_wells"
