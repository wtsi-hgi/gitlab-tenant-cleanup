import os
import re
import unittest

from datetime import timedelta

from logging import getLevelName

from openstack_tenant_cleanup.configuration import parse_configuration, Configuration, GeneralConfiguration, \
    LogConfiguration, CleanupConfiguration, CleanupAreaConfiguration
from openstack_tenant_cleanup.models import OpenstackCredentials

_SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

_EXAMPLE_FULL_CONFIGURATION_LOCATION = os.path.join(_SCRIPT_DIRECTORY, "config.example.yml")
_EXAMPLE_FULL_CONFIGURATION = Configuration(
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
    TODO
    """
    def test_with_full_config(self):
        configuration = parse_configuration(_EXAMPLE_FULL_CONFIGURATION_LOCATION)
        self.assertEqual(_EXAMPLE_FULL_CONFIGURATION, configuration)


if __name__ == "__main__":
    unittest.main()
