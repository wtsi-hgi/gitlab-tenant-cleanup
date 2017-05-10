import logging
from concurrent.futures import ThreadPoolExecutor

from typing import List, Iterable, Tuple, Collection, Callable, Type, Dict

from openstacktenantcleaner.common import create_human_identifier
from openstacktenantcleaner.configuration import Configuration
from openstacktenantcleaner.detectors import PreventDeleteDetector
from openstacktenantcleaner.managers import Manager, OpenstackKeypairManager
from openstacktenantcleaner.models import OpenstackItem
from openstacktenantcleaner.tracking import Tracker

ItemAndReasons = Tuple[OpenstackItem, Collection[str]]
DeleteSetup = Tuple[OpenstackItem, Callable[[OpenstackItem], None]]
CleanUpPlans = List[Dict[Type[Manager],
                         Tuple[Collection[DeleteSetup], Collection[ItemAndReasons], Collection[ItemAndReasons]]]]

_logger = logging.getLogger(__name__)


def create_clean_up_plans(configuration: Configuration, tracker: Tracker, dry_run: bool=True) -> CleanUpPlans:
    """
    Creates plans on what needs to be cleaned up based on the given configuration.
    :param configuration: the clean-up configuration
    :param tracker: OpenStack item tracker
    :param dry_run: will not plan to delete anything if `True`
    :return: the created clean-up plans
    """
    plans: CleanUpPlans = []

    for clean_up_configuration in configuration.clean_up_configurations:
        clean_up_areas_plans = {}

        for manager_type, prevent_delete_detectors in clean_up_configuration.areas.items():
            # Need to use all credentials when cleaning up keys, as they can only be removed by the account that created
            # them
            credentials_to_use = [clean_up_configuration.credentials[0]] if manager_type != OpenstackKeypairManager \
                else clean_up_configuration.credentials

            all_area_delete_setups: List[DeleteSetup] = []
            all_area_marked_for_deletion: List[ItemAndReasons] = []
            all_area_not_marked_for_deletion: List[ItemAndReasons] = []

            for credentials in credentials_to_use:
                manager = manager_type(credentials)
                marked_for_deletion, not_marked_for_deletion = _create_area_report(
                    manager, prevent_delete_detectors, tracker)

                if not dry_run:
                    for item, _ in marked_for_deletion:
                        delete_setup: DeleteSetup = (item, _create_delete(manager))
                        all_area_delete_setups.append(delete_setup)
                all_area_marked_for_deletion += marked_for_deletion
                all_area_not_marked_for_deletion += not_marked_for_deletion

            clean_up_areas_plans[manager_type] = all_area_delete_setups, all_area_marked_for_deletion, \
                                                 all_area_not_marked_for_deletion

        plans.append(clean_up_areas_plans)

    return plans


def execute_plans(plans: CleanUpPlans, max_simultaneous_deletes: int):
    """
    Execute the given clean-up plans.
    :param plans: the clean-up plans
    :param max_simultaneous_deletes: the maximum number of OpenStack items to delete simultaneously. This only applies
    within the method call (it is not global)
    """
    all_delete_setups: List[DeleteSetup] = []
    for plan in plans:
        for _, (delete_setups, _, _) in plan.items():
            all_delete_setups += delete_setups

    with ThreadPoolExecutor(max_simultaneous_deletes) as executor:
        for item, deleter in all_delete_setups:
            _logger.info(f"Deleting item {create_human_identifier(item, True)}")
            executor.submit(deleter, item)

    if len(all_delete_setups) > 0:
        _logger.info(f"{len(all_delete_setups)} item(s) deleted")
        _logger.debug(f"Deleted items: {[create_human_identifier(item, True) for item, _ in all_delete_setups]}")


def create_human_explanation(plans: CleanUpPlans) -> str:
    """
    Creates a human readable explanation of the given cleanup plans.
    :param plans: the plans to explain
    :return: human readable explanation
    """
    lines: List[str] = []
    for i in range(len(plans)):
        lines.append(f"In cleanup configuration number {i +1}:")
        proposal = plans[i]

        for manager_type, (delete_setups, marked_for_deletion, not_marked_for_deletion) in proposal.items():
            for item, reasons in marked_for_deletion:
                lines.append(f"Deleting item {create_human_identifier(item, True)} as not prevented: {reasons}")
            for item, reasons in not_marked_for_deletion:
                lines.append(f"Not deleting item {create_human_identifier(item, True)} as prevented: {reasons}")

        lines.append("")

    return "\n".join(lines)


def _create_area_report(manager: Manager, prevent_delete_detectors: Iterable[PreventDeleteDetector], tracker: Tracker) \
        -> Tuple[List[ItemAndReasons], List[ItemAndReasons]]:
    """
    Creates a report of what can be cleaned up in an area controlled by the given manager.
    :param manager: the OpenStack area manager, where the area could be instances, keys, etc.
    :param prevent_delete_detectors: the detectors that are to be used to determine if an item should not be deleted
    :param tracker: OpenStack item tracker
    :return: tuple where the first item is a list of OpenStack items that have been identified as can be deleted, along 
    with the reasoning for this decision, and the second a list and reasoning of OpenStack items that should not be 
    deleted 
    """
    items = set(manager.get_all())
    registered_identifiers = set(tracker.get_registered_identifiers(item_type=manager.item_type))

    new_items = {item for item in items if item.identifier not in registered_identifiers}
    tracker.register(new_items)

    old_items_identifiers = registered_identifiers - {item.identifier for item in items}
    tracker.unregister(old_items_identifiers)

    not_marked_for_deletion: List[ItemAndReasons] = []
    marked_for_deletion: List[ItemAndReasons] = []

    for item in items:
        not_to_delete_reasons: List[str] = []
        to_delete_reasons: List[str] = []

        for delete_prevent_detector in prevent_delete_detectors:
            delete_prevented, reason = delete_prevent_detector(item, manager.openstack_credentials, tracker)
            if delete_prevented:
                not_to_delete_reasons.append(reason)
            else:
                to_delete_reasons.append(reason)

        if len(not_to_delete_reasons) > 0:
            not_marked_for_deletion.append((item, not_to_delete_reasons))
        else:
            marked_for_deletion.append((item, to_delete_reasons))

    return marked_for_deletion, not_marked_for_deletion


def _create_delete(manager: Manager) -> Callable[[OpenstackItem], None]:
    """
    Creates a method that will use the given manager to delete a given item.
    :param manager: the manager that will perform the delete
    :return: the created method
    """
    def delete(to_delete: OpenstackItem):
        try:
            assert manager.item_type == type(to_delete)
            manager.delete(item=to_delete)
        except Exception as e:
            _logger.error(e)
            raise
    return delete
