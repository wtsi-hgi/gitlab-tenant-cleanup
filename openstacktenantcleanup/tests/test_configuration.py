import os
import unittest
from datetime import timedelta
from logging import getLevelName

from openstacktenantcleanup.configuration import parse_configuration, GeneralConfiguration, LoggingConfiguration
from openstacktenantcleanup.managers import OpenstackInstanceManager, OpenstackKeypairManager, OpenstackImageManager
from openstacktenantcleanup.models import OpenstackCredentials

_RESOURCE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")

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

        self.assertEquals(_EXAMPLE_VALID_GENERAL_CONFIGURATION, configuration.general_configuration)
        self.assertEquals(1, len(configuration.cleanup_configurations))

        cleanup_configuration = configuration.cleanup_configurations[0]
        self.assertEquals(_EXAMPLE_VALID_CREDENTIALS, cleanup_configuration.credentials)

        cleanup_areas = cleanup_configuration.cleanup_areas
        self.assertEquals(3, len(cleanup_areas))

        instance_prevent_delete_detectors = cleanup_areas[OpenstackInstanceManager]
        self.assertEquals(2, len(instance_prevent_delete_detectors))

        image_prevent_delete_detectors = cleanup_areas[OpenstackImageManager]
        self.assertEquals(4, len(image_prevent_delete_detectors))

        keypair_prevent_delete_detectors = cleanup_areas[OpenstackKeypairManager]
        self.assertEquals(3, len(keypair_prevent_delete_detectors))



if __name__ == "__main__":
    unittest.main()
