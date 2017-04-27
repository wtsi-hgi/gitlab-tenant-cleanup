from datetime import timedelta
from typing import Callable, Tuple, Pattern, Iterable

from openstacktenantcleanup.managers import OpenstackInstanceManager
from openstacktenantcleanup.models import OpenstackItem, OpenstackCredentials, OpenstackImage, OpenstackKeyPair
from openstacktenantcleanup.tracking import Tracker

ShouldPreventDeleteAndReason = Tuple[bool, str]
PreventDeleteDetector = Callable[[OpenstackItem, OpenstackCredentials, Tracker], ShouldPreventDeleteAndReason]


def _create_common_message(item: OpenstackItem, include_type: bool=False) -> str:
    """
    TODO
    :param item: 
    :param include_type: 
    :return: 
    """
    type_message = f"of type \"{type(item).__name__}\" " if include_type else ""
    return f"{type_message}with id \"{item.identifier}\" and name \"{item.name}\""


def prevent_delete_protected_image_detector(image: OpenstackImage, openstack_credentials: OpenstackCredentials,
                                            tracker: Tracker) -> ShouldPreventDeleteAndReason:
    """
    Detects when an image delete should be prevented because the OpenStack image is marked as protected.
    :param image: the image of interest
    :param openstack_credentials: credentials to access OpenStack
    :param tracker: OpenStack item history tracker
    :return: whether to prevent deletion of the item and the reason for the decision
    """
    return image.protected, f"Image {_create_common_message(image)} is {'' if image.protected else 'not'} marked on " \
                            f"OpenStack as protected"


def prevent_delete_image_in_use_detector(image: OpenstackImage, openstack_credentials: OpenstackCredentials,
                                         tracker: Tracker) -> ShouldPreventDeleteAndReason:
    """
    Detects when an image delete should be prevented because the image is in use by an OpenStack instance. 
    :param image: the image of interest
    :param openstack_credentials: credentials to access OpenStack
    :param tracker: OpenStack item history tracker
    :return: whether to prevent deletion of the item and the reason for the decision
    """
    common_message = _create_common_message(image)
    instance_manager= OpenstackInstanceManager(openstack_credentials)
    instances = instance_manager.get_all()
    for instance in instances:
        # TODO: Check that both are the same ID type here
        if instance.image == image.identifier:
            return True, f"Image {common_message} cannot be deleted because it is in use by the instance " \
                         f"{_create_common_message(instance)}"
    return False, f"No instances are using the image {common_message}"


def prevent_delete_key_pair_in_use_detector(key_pair: OpenstackKeyPair, openstack_credentials: OpenstackCredentials,
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
            return True, f"Key pair \"{key_pair.name}\" in use by instance {_create_common_message(instance)}"
    return False, "No instances are using the key pair \"{key_pair.name}\""


def create_delete_if_older_than_detector(age: timedelta) -> PreventDeleteDetector:
    """
    Creates a detector that prevents an item from being deleted if younger (or equal) to the given age.
    :param age: the age after which items can be deleted
    :return: the created detector
    """
    def detector(item: OpenstackItem, credentials: OpenstackCredentials, tracker: Tracker):
        common_message = _create_common_message(item, include_type=True)
        item_age = tracker.get_age(item)
        prevent_delete = item_age <= age
        return prevent_delete, f"Item {common_message} age: {item_age} - {'not ' if prevent_delete else ''}deleting " \
                               f"as {'not ' if prevent_delete else ''}older than: {age}"

    return detector


def created_exclude_detector(excludes: Iterable[Pattern]) -> PreventDeleteDetector:
    """
    Creates a detector that prevents an image from being deleted if its name matches on one of the given regexes.
    :param excludes: the exclude regexes
    :return: the created detector
    """
    def detector(item: OpenstackItem, credentials: OpenstackCredentials, tracker: Tracker):
        common_message = _create_common_message(item, include_type=True)
        for exclude in excludes:
            if exclude.fullmatch(item.name) is not None:
                return True, f"Exclude matched for item {common_message}: {exclude.pattern}"
        return False, f"No excludes matched for item {common_message}: {[exclude.pattern for exclude in excludes]}"

    return detector
