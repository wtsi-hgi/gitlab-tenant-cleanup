from datetime import timedelta

from typing import Callable, Tuple, Pattern, Iterable

from openstacktenantcleanup.common import create_human_identifier
from openstacktenantcleanup.managers import OpenstackInstanceManager
from openstacktenantcleanup.models import OpenstackItem, OpenstackCredentials, OpenstackImage, OpenstackKeypair
from openstacktenantcleanup.tracking import Tracker

ShouldPreventDeleteAndReason = Tuple[bool, str]
PreventDeleteDetector = Callable[[OpenstackItem, OpenstackCredentials, Tracker], ShouldPreventDeleteAndReason]


def prevent_delete_protected_image_detector(image: OpenstackImage, openstack_credentials: OpenstackCredentials,
                                            tracker: Tracker) -> ShouldPreventDeleteAndReason:
    """
    Detects when an image delete should be prevented because the OpenStack image is marked as protected.
    :param image: the image of interest
    :param openstack_credentials: credentials to access OpenStack
    :param tracker: OpenStack item history tracker
    :return: whether to prevent deletion of the item and the reason for the decision
    """
    return image.protected, f"Image is {'' if image.protected else 'not '}marked on OpenStack as protected"


def prevent_delete_image_in_use_detector(image: OpenstackImage, openstack_credentials: OpenstackCredentials,
                                         tracker: Tracker) -> ShouldPreventDeleteAndReason:
    """
    Detects when an image delete should be prevented because the image is in use by an OpenStack instance. 
    :param image: the image of interest
    :param openstack_credentials: credentials to access OpenStack
    :param tracker: OpenStack item history tracker
    :return: whether to prevent deletion of the item and the reason for the decision
    """
    instance_manager = OpenstackInstanceManager(openstack_credentials)
    instances = instance_manager.get_all()
    for instance in instances:
        # TODO: Check that both are the same ID type here
        if instance.image == image.identifier:
            return True, f"Image cannot be deleted because it is in use by the instance " \
                         f"{create_human_identifier(instance)}"
    return False, f"No instances are using the image"


def prevent_delete_key_pair_in_use_detector(key_pair: OpenstackKeypair, openstack_credentials: OpenstackCredentials,
                                            tracker: Tracker) -> ShouldPreventDeleteAndReason:
    """
    Detects when an key-pair delete should be prevented because it is in use by an OpenStack instance.
    :param key_pair: 
    :param openstack_credentials: credentials to access OpenStack
    :param tracker: OpenStack item history tracker
    :return: whether to prevent deletion of the item and the reason for the decision
    """
    instance_manager = OpenstackInstanceManager(openstack_credentials)
    for instance in instance_manager.get_all():
        if instance.key_name == key_pair.name:
            return True, f"Key pair in use by instance {create_human_identifier(instance)}"
    return False, "No instances are using the key pair"


def create_delete_if_older_than_detector(age: timedelta) -> PreventDeleteDetector:
    """
    Creates a detector that prevents an item from being deleted if younger (or equal) to the given age.
    :param age: the age after which items can be deleted
    :return: the created detector
    """
    def detector(item: OpenstackItem, credentials: OpenstackCredentials, tracker: Tracker):
        item_age = tracker.get_age(item)
        prevent_delete = item_age <= age
        return prevent_delete, f"Item age: {item_age} - {'not ' if prevent_delete else ''}older than: {age}"

    return detector


def created_exclude_detector(excludes: Iterable[Pattern]) -> PreventDeleteDetector:
    """
    Creates a detector that prevents an image from being deleted if its name matches on one of the given regexes.
    :param excludes: the exclude regexes
    :return: the created detector
    """
    def detector(item: OpenstackItem, credentials: OpenstackCredentials, tracker: Tracker):
        for exclude in excludes:
            if exclude.fullmatch(item.name) is not None:
                return True, f"Exclude matched: {exclude.pattern}"
        return False, f"Excludes not matched: {[exclude.pattern for exclude in excludes]}"

    return detector
