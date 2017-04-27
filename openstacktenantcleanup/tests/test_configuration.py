import os
import re
import unittest
from datetime import timedelta
from logging import getLevelName

from openstacktenantcleanup.configuration import parse_configuration, Configuration, GeneralConfiguration, \
    LogConfiguration, CleanupConfiguration, CleanupAreaConfiguration
from openstacktenantcleanup.models import OpenstackCredentials

_RESOURCE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")

_EXAMPLE_VALID_CONFIGURATION_LOCATION = os.path.join(_RESOURCE_DIRECTORY, "valid.config.yml")
_EXAMPLE_VALID_CONFIGURATION = Configuration(
    general_configuration=GeneralConfiguration(
        run_period=timedelta(hours=1),
        log=LogConfiguration(
            location="/my-log",
            level=getLevelName("WARN")
        )
    ),
    cleanup_configurations=[
        CleanupConfiguration(
            credentials=[OpenstackCredentials(
                auth_url="http://example.com:5000/v2.0",
                tenant="my-tenant",
                username="my-username",
                password="my-password"
            )],
            instance_cleanup_configuration=CleanupAreaConfiguration(
                remove_if_older_than=timedelta(days=1),
                excludes=[re.compile("my-special-instance.*")]
            ),
            image_cleanup_configuration=CleanupAreaConfiguration(
                remove_only_if_unused=True,
                remove_if_older_than=timedelta(days=31),
                excludes=[re.compile("my-special-image[0-9]+")]
            ),
            keypair_cleanup_configuration = CleanupAreaConfiguration(
                remove_only_if_unused=True,
                remove_if_older_than=timedelta(hours=1),
                excludes=[re.compile("my-special-key-pair")]
            )
        )
    ]
)


class TestParseConfiguration(unittest.TestCase):
    """
    Tests for `parse_configuration`.
    """
    def test_with_full_config(self):
        configuration = parse_configuration(_EXAMPLE_VALID_CONFIGURATION_LOCATION)
        self.assertEquals(_EXAMPLE_VALID_CONFIGURATION, configuration)


if __name__ == "__main__":
    unittest.main()
