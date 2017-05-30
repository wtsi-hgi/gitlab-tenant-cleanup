import unittest

from openstacktenantcleaner.managers import OpenstackInstanceManager, OpenstackImageManager, OpenstackKeypairManager
from openstacktenantcleaner.planning import sort_clean_up_areas


class TestSortCleanUpAreas(unittest.TestCase):
    """
    Tests for `sort_clean_up_areas`.
    """
    def test_sort_with_no_items(self):
        self.assertCountEqual([], sort_clean_up_areas([]))

    def test_sort_with_one_item(self):
        item = (OpenstackInstanceManager, [])
        self.assertCountEqual([item], sort_clean_up_areas([item]))

    def test_sort_with_no_order(self):
        items = [(item, []) for item in [OpenstackKeypairManager, OpenstackImageManager]]
        self.assertCountEqual(items, sort_clean_up_areas(items))

    def test_sort_with_order(self):
        items = [(item, []) for item in [OpenstackKeypairManager, OpenstackInstanceManager, OpenstackImageManager]]
        ordered = sort_clean_up_areas(items)
        self.assertCountEqual(items, ordered)
        self.assertEquals(OpenstackInstanceManager, ordered[0][0])


if __name__ == "__main__":
    unittest.main()
