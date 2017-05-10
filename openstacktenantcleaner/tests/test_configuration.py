import os
import unittest
from datetime import timedelta
from logging import getLevelName

from openstacktenantcleaner.configuration import parse_configuration, GeneralConfiguration, LoggingConfiguration
from openstacktenantcleaner.managers import OpenstackInstanceManager, OpenstackKeypairManager, OpenstackImageManager
from openstacktenantcleaner.models import OpenstackCredentials

_RESOURCE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_resources")

_EXAMPLE_VALID_CONFIGURATION_LOCATION = os.path.join(_RESOURCE_DIRECTORY, "valid.config.yml")
_EXAMPLE_VALID_GENERAL_CONFIGURATION = GeneralConfiguration(
    run_period=timedelta(hours=1),
    logging_configuration=LoggingConfiguration(
        location="/my-log",
        level=getLevelName("WARN")
    ),
    tracking_database="tracking.sqlite",
    max_simultaneous_deletes=8
)
_EXAMPLE_VALID_CREDENTIALS = [OpenstackCredentials(
    auth_url="http://example.com:5000/v2.0/",
    tenant="my-tenant",
    username="my-username",
    password="my-password"
)]


class TestParseConfiguration(unittest.TestCase):
    """
    Tests for `parse_configuration`.
    """
    def test_parse_valid_configuration(self):
        configuration = parse_configuration(_EXAMPLE_VALID_CONFIGURATION_LOCATION)

        self.assertEqual(_EXAMPLE_VALID_GENERAL_CONFIGURATION, configuration.general_configuration)
        self.assertEqual(1, len(configuration.clean_up_configurations))

        clean_up_configuration = configuration.clean_up_configurations[0]
        self.assertEqual(_EXAMPLE_VALID_CREDENTIALS, clean_up_configuration.credentials)

        areas = clean_up_configuration.areas
        self.assertEqual(3, len(areas))

        instance_prevent_delete_detectors = areas[OpenstackInstanceManager]
        self.assertEqual(2, len(instance_prevent_delete_detectors))

        image_prevent_delete_detectors = areas[OpenstackImageManager]
        self.assertEqual(4, len(image_prevent_delete_detectors))

        keypair_prevent_delete_detectors = areas[OpenstackKeypairManager]
        self.assertEqual(3, len(keypair_prevent_delete_detectors))


if __name__ == "__main__":
    unittest.main()
