import re
from datetime import timedelta
from logging import getLevelName

import yaml
from boltons.timeutils import parse_timedelta
from hgicommon.models import Model
from typing import Pattern, List

from openstacktenantcleanup.models import OpenstackCredentials

_GENERAL_PROPERTY = "general"
_GENERAL_RUN_EVERY_PROPERTY = "run-every"
_GENERAL_LOG_PROPERTY = "log"
_GENERAL_LOG_LOCATION_PROPERTY = "location"
_GENERAL_LOG_LEVEL_PROPERTY = "level"
_CLEANUP_PROPERTY = "cleanup"
_CLEANUP_OPENSTACK_AUTH_URL_PROPERTY = "openstack_auth_url"
_CLEANUP_CREDENTIALS_PROPERTY = "credentials"
_CLEANUP_CREDENTIALS_USERNAME_PROPERTY = "username"
_CLEANUP_CREDENTIALS_PASSWORD_PROPERTY = "password"
_CLEANUP_TENANT_PROPERTY = "tenant"
_CLEANUP_INSTANCES_PROPERTY = "instances"
_CLEANUP_IMAGES_PROPERTY = "images"
_CLEANUP_KEY_PAIRS_PROPERTY = "key-pairs"
_CLEANUP_REMOVE_IF_OLDER_THAN_PROPERTY = "remove-if-older-than"
_CLEANUP_EXCLUDE_PROPERTY = "exclude"
_CLEANUP_REMOVE_ONLY_IF_UNUSED_PROPERTY = "remove-only-if-unused"


class CleanupAreaConfiguration(Model):
    """
    Configuration for how an area (e.g. images, key-pairs) is to be cleaned.
    """
    def __init__(self, remove_if_older_than: timedelta, excludes: List[Pattern], remove_only_if_unused: bool=True):
        self.remove_if_older_than = remove_if_older_than
        self.excludes = excludes
        self.remove_only_if_unused = remove_only_if_unused


class CleanupConfiguration(Model):
    """
    Model
    """
    def __init__(self, credentials: List[OpenstackCredentials]=None,
                 instance_cleanup_configuration: CleanupAreaConfiguration=None,
                 image_cleanup_configuration: CleanupAreaConfiguration=None,
                 keypair_cleanup_configuration: CleanupAreaConfiguration=None):
        self.credentials = credentials if credentials is not None else []
        self.instance_cleanup_configuration = instance_cleanup_configuration
        self.image_cleanup_configuration = image_cleanup_configuration
        self.keypair_cleanup_configuration = keypair_cleanup_configuration


class LogConfiguration(Model):
    """
    Configuration for logging.
    """
    def __init__(self, location: str=None, level: int=None):
        self.location = location
        self.level = level


class GeneralConfiguration(Model):
    """
    General configuration.
    """
    def __init__(self, run_period: timedelta=None, log: LogConfiguration=None):
        self.run_period = run_period
        self.log = log


class Configuration(Model):
    """
    Full configuration.
    """
    def __init__(self, general_configuration: GeneralConfiguration, cleanup_configurations: List[CleanupConfiguration]):
        self.general_configuration = general_configuration
        self.cleanup_configurations = cleanup_configurations


def _convert_to_timedelta(raw_timedelta: str) -> timedelta:
    """
    Converts a human readable time delta (e.g. "1h") to the equivalent Python `timedelta`.
    :param raw_timedelta: the human readable timestamp
    :return: the equivalent Python `timedelta`
    """
    return parse_timedelta(raw_timedelta)


def parse_configuration(location: str):
    """
    Parses the configuration in the given location.
    :param location: the location of the configuration that is to be parsed
    :return: parsed configuration
    """
    with open(location, "r") as file:
        raw_configuration = yaml.load(file)

    raw_general = raw_configuration[_GENERAL_PROPERTY]
    general_configuration = GeneralConfiguration(
        run_period=_convert_to_timedelta(raw_general[_GENERAL_RUN_EVERY_PROPERTY]),
        log=LogConfiguration(
            location=raw_general[_GENERAL_LOG_PROPERTY][_GENERAL_LOG_LOCATION_PROPERTY],
            level=getLevelName(raw_general[_GENERAL_LOG_PROPERTY][_GENERAL_LOG_LEVEL_PROPERTY].upper())
        )
    )

    cleanup_configuration = CleanupConfiguration()
    for raw_cleanup in raw_configuration[_CLEANUP_PROPERTY]:
        raw_credentials = raw_cleanup[_CLEANUP_CREDENTIALS_PROPERTY]
        for raw_credential in raw_credentials:
            cleanup_configuration.credentials.append(OpenstackCredentials(
                auth_url=raw_cleanup[_CLEANUP_OPENSTACK_AUTH_URL_PROPERTY],
                tenant=raw_cleanup[_CLEANUP_TENANT_PROPERTY],
                username=raw_credential[_CLEANUP_CREDENTIALS_USERNAME_PROPERTY],
                password=raw_credential[_CLEANUP_CREDENTIALS_PASSWORD_PROPERTY],
            ))

        if _CLEANUP_IMAGES_PROPERTY in raw_cleanup:
            raw_images = raw_cleanup[_CLEANUP_IMAGES_PROPERTY]
            cleanup_configuration.image_cleanup_configuration = CleanupAreaConfiguration(
                remove_if_older_than=_convert_to_timedelta(raw_images[_CLEANUP_REMOVE_IF_OLDER_THAN_PROPERTY]),
                excludes=[re.compile(exclude) for exclude in raw_images[_CLEANUP_EXCLUDE_PROPERTY]])
    
        if _CLEANUP_INSTANCES_PROPERTY in raw_cleanup:
            raw_instances = raw_cleanup[_CLEANUP_INSTANCES_PROPERTY]
            cleanup_configuration.instance_cleanup_configuration = CleanupAreaConfiguration(
                remove_if_older_than=_convert_to_timedelta(raw_instances[_CLEANUP_REMOVE_IF_OLDER_THAN_PROPERTY]),
                excludes=[re.compile(exclude) for exclude in raw_instances[_CLEANUP_EXCLUDE_PROPERTY]])

        if _CLEANUP_KEY_PAIRS_PROPERTY in raw_cleanup:
            raw_keypairs = raw_cleanup[_CLEANUP_KEY_PAIRS_PROPERTY]
            cleanup_configuration.keypair_cleanup_configuration = CleanupAreaConfiguration(
                remove_only_if_unused=raw_keypairs[_CLEANUP_REMOVE_ONLY_IF_UNUSED_PROPERTY],
                remove_if_older_than=_convert_to_timedelta(raw_keypairs[_CLEANUP_REMOVE_IF_OLDER_THAN_PROPERTY]),
                excludes=[re.compile(exclude) for exclude in raw_keypairs[_CLEANUP_EXCLUDE_PROPERTY]])

    return Configuration(
        general_configuration=general_configuration,
        cleanup_configurations=[cleanup_configuration]
    )
