from typing import Sequence, Iterable

from hgicommon.models import Model
from sequencescape._sqlalchemy._models import SQLAlchemySample, SQLAlchemyStudy, SQLAlchemyLibrary, \
    SQLAlchemyWell, SQLAlchemyMultiplexedLibrary, SQLAlchemyModel
from sequencescape.models import Library, Study, Sample, Well, MultiplexedLibrary


_SQLALCHEMY_TO_POPO_CONVERSIONS = {
    SQLAlchemySample: Sample,
    SQLAlchemyStudy: Study,
    SQLAlchemyLibrary: Library,
    SQLAlchemyWell: Well,
    SQLAlchemyMultiplexedLibrary: MultiplexedLibrary
}


def get_equivalent_popo_model_type(sqlalchemy_type: type) -> type:
    """
    Gets the equivalent Plain Old Python Object (POPO) type for the given SQLAlchemy model type.
    :param sqlalchemy_type: the type of SQLAlchemy model to get_by_path equivalent POPO for
    :return: the equivalent type of POPO for the given SQLAlchemy model type. `None` if no equivalent model is known
    """
    if sqlalchemy_type not in _SQLALCHEMY_TO_POPO_CONVERSIONS:
        raise ValueError("No conversion of SQLAlchemy model of type `%s` known" % sqlalchemy_type)

    return _SQLALCHEMY_TO_POPO_CONVERSIONS[sqlalchemy_type]


def get_equivalent_sqlalchemy_model_type(popo_type: type) -> type:
    """
    Gets the equivalent SQLAlchemy model type for the given Plain Old Python Object (POPO).
    :param popo_type: the type of POPO model to get_by_path equivalent SQLAlchemy model for
    :return: the equivalent type of SQLAlchemy model to the given POPO. `None` if no equivalent model is known
    """
    for key, value in _SQLALCHEMY_TO_POPO_CONVERSIONS.items():
        if value == popo_type:
            return key
    raise ValueError("No conversion of POPO model of type `%s` known" % popo_type)


def convert_to_popo_model(sqlalchemy_model: SQLAlchemyModel) -> Model:
    """
    Converts the given SQLAlchemy model into an equivalent POPO model thus removing the coupling to the underlying ORM.
    Raises exception if cannot convert.
    :param sqlalchemy_model: the SQLAlchemy model to convert
    :return: an equivalent POPO model
    """
    type = sqlalchemy_model.__class__
    convert_to_type = get_equivalent_popo_model_type(type)

    if convert_to_type is None:
        raise ValueError("SQLAlchemy models of type %s have not been setup for automatic conversion" % type)

    converted = convert_to_type()
    assert issubclass(converted.__class__, Model)

    for property_name, value in vars(sqlalchemy_model).items():
        if property_name in converted.__dict__:
            converted.__dict__[property_name] = value

    return converted


def convert_to_popo_models(sqlalchemy_models: Iterable[SQLAlchemyModel]) -> Sequence[Model]:
    """
    Converts the given SQLAlchemy models into an equivalent POPO models thus removing the coupling to the underlying
    ORM.
    :param sqlalchemy_models: the SQLAlchemy models to convert
    :return: an equivalent POPO models
    """
    return [convert_to_popo_model(x) for x in sqlalchemy_models]


def convert_to_sqlalchemy_model(model: Model) -> SQLAlchemyModel:
    """
    Converts the given POPO model into an equivalent SQLAlchemy model. Raises exception if cannot convert.
    :param model: the POPO model to convert
    :return: the equivalent SQLAlchemy model
    """
    type = model.__class__
    convert_to_type = get_equivalent_sqlalchemy_model_type(type)    # type: type

    if convert_to_type is None:
        raise ValueError("Models of type %s have not been setup for automatic conversion to SQLAlchemy models" % type)

    converted = convert_to_type()
    assert issubclass(converted.__class__, SQLAlchemyModel)

    for property_name, value in vars(model).items():
        converted.__dict__[property_name] = value

    return converted


def convert_to_sqlalchemy_models(models: Iterable[Model]) -> Sequence[SQLAlchemyModel]:
    """
    Converts the given POPO models into equivalent SQLAlchemy models.
    :param models: the POPO models to convert
    :return: the equivalent SQLAlchemy models
    """
    return [convert_to_sqlalchemy_model(x) for x in models]
