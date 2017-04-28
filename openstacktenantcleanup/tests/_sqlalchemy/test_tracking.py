import unittest
from datetime import datetime, timedelta

from openstacktenantcleanup._sqlalchemy.tracking import SqlTracker
from openstacktenantcleanup.external.sequencescape.stub_database import create_stub_database
from openstacktenantcleanup.models import OpenstackKeypair, OpenstackImage, OpenstackInstance


class TestSqlTracker(unittest.TestCase):
    """
    Tests for `SqlTracker`.
    """
    def setUp(self):
        database_location, dialect = create_stub_database()
        self.tracker = SqlTracker(f"{dialect}:///{database_location}")

    def test_get_age_when_does_not_exist(self):
        item = OpenstackKeypair(identifier="123")
        self.assertIsNone(self.tracker.get_age(item))

    def test_get_registered_identifiers(self):
        items = [OpenstackKeypair(identifier="1"), OpenstackImage(identifier="2"), OpenstackInstance(identifier="3")]
        self.tracker.register(items)
        registered = self.tracker.get_registered_identifiers()
        self.assertEquals(set(registered), {item.identifier for item in items})

    def test_get_registered_identifiers_of_type(self):
        test_type = OpenstackKeypair
        items = {test_type(identifier=str(i)) for i in range(10)}
        self.tracker.register(items)
        registered = self.tracker.get_registered_identifiers(item_type=test_type)
        self.assertEqual(set(registered), {item.identifier for item in items})

    def test_register_with_created_time(self):
        item = OpenstackImage(identifier="123", created_at=datetime(2016, 1, 1))
        start_time = datetime.now()
        self.tracker.register(item)
        age = self.tracker.get_age(item)
        end_time = datetime.now()

        minimum_age = start_time - item.created_at
        maximum_age = end_time - item.created_at

        self.assertGreaterEqual(age, minimum_age)
        self.assertLessEqual(age, maximum_age)

    def test_register_without_created_time(self):
        item = OpenstackKeypair(identifier="123")
        start_time = datetime.now()
        self.tracker.register(item)
        age = self.tracker.get_age(item)
        end_time = datetime.now()

        maximum_age = end_time - start_time

        self.assertGreaterEqual(age, timedelta(0))
        self.assertLessEqual(age, maximum_age)

    def test_register_when_already_registered(self):
        item = OpenstackKeypair(identifier="123")
        self.tracker.register(item)
        self.tracker.register(item)

    def test_unregister_when_not_exists(self):
        item = OpenstackKeypair(identifier="123")
        self.tracker.unregister(item)

    def test_unregister(self):
        item = OpenstackKeypair(identifier="123")
        self.tracker.register(item)
        self.tracker.unregister(item)
        self.assertIsNone(self.tracker.get_age(item))


if __name__ == "__main__":
    unittest.main()
