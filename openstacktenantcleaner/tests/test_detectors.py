import unittest

from openstacktenantcleaner.detectors import prevent_delete_protected_image_detector
from openstacktenantcleaner.models import OpenstackImage, OpenstackCredentials


class TestPreventDeleteProtectedImageDetector(unittest.TestCase):
    """
    Tests for `prevent_delete_protected_image_detector`.
    """
    def test_not_protected(self):
        prevented, reasons = prevent_delete_protected_image_detector(OpenstackImage(protected=False), None, None, set())
        self.assertFalse(prevented)

    def test_protected(self):
        prevented, reasons = prevent_delete_protected_image_detector(OpenstackImage(protected=True), None, None, set())
        self.assertTrue(prevented)


if __name__ == "__main__":
    unittest.main()
