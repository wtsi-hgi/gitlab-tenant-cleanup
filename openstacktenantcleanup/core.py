import logging

from typing import List

from openstacktenantcleanup.configuration import CleanupAreaConfiguration, Configuration
from openstacktenantcleanup.managers import Manager, OpenstackKeyPairManager
from openstacktenantcleanup.models import OpenstackItem
from openstacktenantcleanup.tracking import Tracker

# FIXME
_logger = logging.root


def clean_up(configuration: Configuration, tracker: Tracker):
    """
    TODO
    :param configuration: 
    :param tracker: 
    :return: 
    """
    # TODO: cleanup in order: instances first, others next
    for cleanup_configuration in configuration.cleanup_configurations:
        for manager_type, cleanup_area_configuration in cleanup_configuration.cleanup_areas.items():
            # Need to use all credentials when cleaning up keys, as they can only be removed by the account that created
            # them
            credentials_to_use = [cleanup_configuration.credentials[0]] if manager_type != OpenstackKeyPairManager \
                else cleanup_configuration.credentials

            for credentials in credentials_to_use:
                manger = manager_type(credentials)
                clean_up_area(manger, cleanup_area_configuration, tracker)


def clean_up_area(manager: Manager, cleanup_area_configuration: CleanupAreaConfiguration, tracker: Tracker):
    """
    TODO
    :param manager: 
    :param cleanup_area_configuration: 
    :param tracker: 
    :return: 
    """
    items = set(manager.get_all())
    registered = set(tracker.get_registered_identifiers(item_type=manager.item_type))

    new_items = items - registered
    tracker.register(new_items)

    old_items = registered - items
    tracker.unregister(old_items)

    marked_for_deletion: List[OpenstackItem] = []
    for item in items:
        delete_prevented = False
        for delete_prevent_detector in cleanup_area_configuration.prevent_delete_detectors:
            delete_prevented, reason = delete_prevent_detector(item, manager.openstack_credentials, tracker)
            if delete_prevented:
                break
        if not delete_prevented:
            marked_for_deletion.append(item)

    print(f"Marked for deletion: {marked_for_deletion}")


if __name__ == "__main__":
    pass
