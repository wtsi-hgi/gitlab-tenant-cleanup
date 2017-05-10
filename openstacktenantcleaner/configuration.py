import os
import re
from datetime import timedelta
from logging import getLevelName

import yaml
from boltons.timeutils import parse_timedelta
from typing import List, Iterable, Type, Dict, Any

from openstacktenantcleaner.common import get_absolute_path_relative_to
from openstacktenantcleaner.detectors import PreventDeleteDetector, prevent_delete_protected_image_detector, \
    prevent_delete_image_in_use_detector, prevent_delete_key_pair_in_use_detector, created_exclude_detector, \
    create_delete_if_older_than_detector
from openstacktenantcleaner.external.hgicommon.models import Model
from openstacktenantcleaner.managers import OpenstackInstanceManager, Manager, OpenstackImageManager, \
    OpenstackKeypairManager
from openstacktenantcleaner.models import OpenstackCredentials

_GENERAL_PROPERTY = "general"
_GENERAL_RUN_EVERY_PROPERTY = "run-every"
_GENERAL_LOGGING_PROPERTY = "log"
_GENERAL_LOG_LOCATION_PROPERTY = "location"
_GENERAL_LOG_LEVEL_PROPERTY = "level"
_GENERAL_TRACKING_DATABASE_PROPERTY = "tracking-database"
_GENERAL_MAX_SIMULTANEOUS_DELETES_PROPERTY = "max-simultaneous-deletes"
_CLEAN_UP_PROPERTY = "cleanup"
_CLEAN_UP_OPENSTACK_AUTH_URL_PROPERTY = "openstack-auth-url"
_CLEAN_UP_CREDENTIALS_PROPERTY = "credentials"
_CLEAN_UP_CREDENTIALS_USERNAME_PROPERTY = "username"
_CLEAN_UP_CREDENTIALS_PASSWORD_PROPERTY = "password"
_CLEAN_UP_TENANT_PROPERTY = "tenant"
_CLEAN_UP_INSTANCES_PROPERTY = "instances"
_CLEAN_UP_IMAGES_PROPERTY = "images"
_CLEAN_UP_KEY_PAIRS_PROPERTY = "key-pairs"
_CLEAN_UP_REMOVE_IF_OLDER_THAN_PROPERTY = "remove-if-older-than"
_CLEAN_UP_EXCLUDE_PROPERTY = "exclude"
_CLEAN_UP_REMOVE_ONLY_IF_UNUSED_PROPERTY = "remove-only-if-unused"

DEFAULT_MAX_SIMULTANEOUS_DELETES = 4


class CleanUpConfiguration(Model):
    """
    Configuration for how a set of areas are to be cleaned.
    """
    def __init__(self, credentials: List[OpenstackCredentials]=None):
        self.credentials = credentials if credentials is not None else []
        self.areas: Dict[Type[Manager], Iterable[PreventDeleteDetector]] = {}


class LoggingConfiguration(Model):
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
    def __init__(self, run_period: timedelta=None, logging_configuration: LoggingConfiguration=None,
                 tracking_database: str=None, max_simultaneous_deletes: int=DEFAULT_MAX_SIMULTANEOUS_DELETES):
        self.run_period = run_period
        self.logging_configuration = logging_configuration
        self.tracking_database = tracking_database
        self.max_simultaneous_deletes = max_simultaneous_deletes


class Configuration(Model):
    """
    Full configuration.
    """
    def __init__(self, general_configuration: GeneralConfiguration, clean_up_configurations: List[CleanUpConfiguration]):
        self.general_configuration = general_configuration
        self.clean_up_configurations = clean_up_configurations


def _create_common_prevent_delete_detectors(parent_property: Dict[str, Any]) -> List[PreventDeleteDetector]:
    """
    Creates delete prevention detectors that are common to all area clean-ups.
    :param parent_property: the area clean-up configuration
    :return: the created delete prevent detectors
    """
    detectors: List[PreventDeleteDetector] = []

    if _CLEAN_UP_EXCLUDE_PROPERTY in parent_property:
        excludes = [re.compile(exclude) for exclude in parent_property[_CLEAN_UP_EXCLUDE_PROPERTY]]
        detectors.append(created_exclude_detector(excludes))

    if _CLEAN_UP_REMOVE_IF_OLDER_THAN_PROPERTY in parent_property:
        delete_if_older_than = parse_timedelta(parent_property[_CLEAN_UP_REMOVE_IF_OLDER_THAN_PROPERTY])
        detectors.append(create_delete_if_older_than_detector(delete_if_older_than))

    return detectors


def parse_configuration(location: str):
    """
    Parses the configuration in the given location.
    :param location: the location of the configuration that is to be parsed
    :return: parsed configuration
    """
    with open(location, "r") as file:
        raw_configuration = yaml.load(file)

    raw_general = raw_configuration[_GENERAL_PROPERTY]

    log_location = raw_general[_GENERAL_LOGGING_PROPERTY][_GENERAL_LOG_LOCATION_PROPERTY]
    if not os.path.isabs(log_location):
        log_location = get_absolute_path_relative_to(log_location, location)
    general_configuration = GeneralConfiguration(
        run_period=parse_timedelta(raw_general[_GENERAL_RUN_EVERY_PROPERTY]),
        logging_configuration=LoggingConfiguration(
            location=log_location,
            level=getLevelName(raw_general[_GENERAL_LOGGING_PROPERTY][_GENERAL_LOG_LEVEL_PROPERTY].upper())
        ),
        tracking_database=raw_general[_GENERAL_TRACKING_DATABASE_PROPERTY],
    )
    if _GENERAL_MAX_SIMULTANEOUS_DELETES_PROPERTY in raw_general:
        general_configuration.max_simultaneous_deletes = raw_general[_GENERAL_MAX_SIMULTANEOUS_DELETES_PROPERTY]

    cleanup_configuration = CleanUpConfiguration()
    for raw_cleanup in raw_configuration[_CLEAN_UP_PROPERTY]:
        raw_credentials = raw_cleanup[_CLEAN_UP_CREDENTIALS_PROPERTY]
        for raw_credential in raw_credentials:
            cleanup_configuration.credentials.append(OpenstackCredentials(
                auth_url=raw_cleanup[_CLEAN_UP_OPENSTACK_AUTH_URL_PROPERTY],
                tenant=raw_cleanup[_CLEAN_UP_TENANT_PROPERTY],
                username=raw_credential[_CLEAN_UP_CREDENTIALS_USERNAME_PROPERTY],
                password=raw_credential[_CLEAN_UP_CREDENTIALS_PASSWORD_PROPERTY],
            ))

        if _CLEAN_UP_IMAGES_PROPERTY in raw_cleanup:
            raw_images = raw_cleanup[_CLEAN_UP_IMAGES_PROPERTY]
            detectors = _create_common_prevent_delete_detectors(raw_images)
            detectors.append(prevent_delete_protected_image_detector)
            detectors.append(prevent_delete_image_in_use_detector)
            cleanup_configuration.areas[OpenstackImageManager] = detectors
    
        if _CLEAN_UP_INSTANCES_PROPERTY in raw_cleanup:
            raw_instances = raw_cleanup[_CLEAN_UP_INSTANCES_PROPERTY]
            detectors = _create_common_prevent_delete_detectors(raw_instances)
            cleanup_configuration.areas[OpenstackInstanceManager] = detectors

        if _CLEAN_UP_KEY_PAIRS_PROPERTY in raw_cleanup:
            raw_keypairs = raw_cleanup[_CLEAN_UP_KEY_PAIRS_PROPERTY]
            detectors = _create_common_prevent_delete_detectors(raw_keypairs)

            if raw_keypairs[_CLEAN_UP_REMOVE_ONLY_IF_UNUSED_PROPERTY]:
                detectors.append(prevent_delete_key_pair_in_use_detector)

            cleanup_configuration.areas[OpenstackKeypairManager] = detectors

    return Configuration(
        general_configuration=general_configuration,
        clean_up_configurations=[cleanup_configuration]
    )
