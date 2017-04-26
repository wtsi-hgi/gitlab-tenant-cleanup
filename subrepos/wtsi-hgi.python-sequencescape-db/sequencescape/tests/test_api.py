import unittest

from sequencescape.api import Connection, connect_to_sequencescape
from sequencescape.mappers import Mapper
from sequencescape.tests.sqlalchemy.stub_database import create_stub_database


class TestConnection(unittest.TestCase):
    """
    Tests for `Connection` class.
    """
    def test_with_valid_database_url(self):
        database_location, dialect = create_stub_database()
        connect_to_sequencescape("%s:///%s" % (dialect, database_location))

    def test_with_no_database_url(self):
        self.assertRaises(ValueError, connect_to_sequencescape, "")

    def test_with_invalid_database_url(self):
        self.assertRaises(ValueError, connect_to_sequencescape, "invalid")

    def test_correct_mapper_properties(self):
        connection = Connection("dialect://host")
        self.assertIsInstance(connection.sample, Mapper)
        self.assertIsInstance(connection.study, Mapper)
        self.assertIsInstance(connection.multiplexed_library, Mapper)
        self.assertIsInstance(connection.library, Mapper)
        self.assertIsInstance(connection.well, Mapper)


class TestConnectToSequencescape(unittest.TestCase):
    """
    Tests for `connect_to_sequencescape` method.
    """
    def test_returns_connection(self):
        database_location = "dialect://HOST"
        connection = connect_to_sequencescape(database_location)
        self.assertIsInstance(connection, Connection)


if __name__ == "__main__":
    unittest.main()
