import urllib.parse

from sequencescape._sqlalchemy.database_connector import SQLAlchemyDatabaseConnector
from sequencescape._sqlalchemy.mappers import SQLAlchemySampleMapper, SQLAlchemyMultiplexedLibraryMapper, \
    SQLAlchemyLibraryMapper, SQLAlchemyWellMapper
from sequencescape._sqlalchemy.mappers import SQLAlchemyStudyMapper


class Connection:
    """
    Connection manager for queries to the Sequencescape database.
    """
    def __init__(self, database_location: str):
        """
        Constructor.
        :param database_location: location of the database as a URL
        """
        parsed_database_location = urllib.parse.urlparse(database_location)
        if parsed_database_location.scheme == "":
            raise ValueError("Database location must define a scheme (%s given)" % database_location)

        database_connector = SQLAlchemyDatabaseConnector(database_location)
        self.sample = SQLAlchemySampleMapper(database_connector)
        self.study = SQLAlchemyStudyMapper(database_connector)
        self.multiplexed_library = SQLAlchemyMultiplexedLibraryMapper(database_connector)
        self.library = SQLAlchemyLibraryMapper(database_connector)
        self.well = SQLAlchemyWellMapper(database_connector)


def connect_to_sequencescape(database_uri: str) -> Connection:
    """
    Creates an object that enables the transfer of data from a Sequencescape database to be made using data mappers.
    Only opens connections when data mappers are used.
    :param database_uri: location of the database as a URL
    :return: object through which connections can be made to the Sequencescape database
    """
    return Connection(database_uri)
