import unittest

from openstacktenantcleaner.common import create_human_identifier, get_absolute_path_relative_to
from openstacktenantcleaner.models import OpenstackInstance

_IDENTIFIER = "my-identifier"
_NAME = "my-name"
_IMAGE = "my-image"
_KEY_PAIR = "my-key"


class TestCreateHumanIdentifier(unittest.TestCase):
    """
    Tests for `create_human_identifier`.
    """
    def setUp(self):
        self.item = OpenstackInstance(identifier=_IDENTIFIER, name=_NAME, image=_IMAGE, key_name=_KEY_PAIR)

    def test_without_type_included(self):
        human_identifier = create_human_identifier(self.item)
        self.assertNotIn(type(self.item).__name__, human_identifier)
        self.assertIn(self.item.identifier, human_identifier)
        self.assertIn(self.item.name, human_identifier)

    def test_with_type_included(self):
        human_identifier = create_human_identifier(self.item, True)
        self.assertIn(type(self.item).__name__, human_identifier)
        self.assertIn(self.item.identifier, human_identifier)
        self.assertIn(self.item.name, human_identifier)


class TestGetAbsolutePathRelativeTo(unittest.TestCase):
    """
    Tests for `get_absolute_path_relative_to`.
    """
    def test_with_absolute_path(self):
        self.assertRaises(ValueError, get_absolute_path_relative_to, "/file", "/path")

    def test_with_relative_path(self):
        self.assertEquals("/path/file", get_absolute_path_relative_to("file", "/path/file"))


if __name__ == "__main__":
    unittest.main()
