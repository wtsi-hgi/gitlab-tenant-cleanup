import os
import tempfile
from typing import Tuple

import atexit
from sqlalchemy import create_engine

from sequencescape._sqlalchemy._models import SQLAlchemyModel


def create_stub_database() -> Tuple[str, str]:
    """
    Creates a stub database with a number of tables found in a Sequencescape database.

    An in-memory database is not used because sqlite in-memory databases are destroyed upon close.
    :return: stub database and the dialect
    """
    def clean_up():
        os.remove(database_location)
    atexit.register(clean_up)

    file_handle, database_location = tempfile.mkstemp()

    dialect = "sqlite"
    engine = create_engine("sqlite:///%s" % database_location)
    SQLAlchemyModel.metadata.create_all(bind=engine)

    return database_location, dialect
