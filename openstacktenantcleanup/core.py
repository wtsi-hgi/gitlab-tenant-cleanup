from typing import List, Iterable, Tuple, Collection, Callable, Type, Dict

from openstacktenantcleanup.common import create_human_identifier
from openstacktenantcleanup.configuration import Configuration
from openstacktenantcleanup.detectors import PreventDeleteDetector
from openstacktenantcleanup.managers import Manager, OpenstackKeypairManager
from openstacktenantcleanup.models import OpenstackItem
from openstacktenantcleanup.tracking import Tracker

ItemAndReasons = Tuple[OpenstackItem, Collection[str]]
DeleteSetup = Tuple[OpenstackItem, Callable[[OpenstackItem], None]]
CleanUpProposal = List[Dict[Type[Manager],
                            Tuple[Collection[DeleteSetup], Collection[ItemAndReasons], Collection[ItemAndReasons]]]]


def create_clean_up_proposals(configuration: Configuration, tracker: Tracker, dry_run: bool=True) -> CleanUpProposal:
    """
    TODO
    :param configuration: 
    :param tracker: 
    :param dry_run: 
    :return: 
    """
    cleaup_proposal: CleanUpProposal = []

    # TODO: cleanup in order: instances first, others next
    for cleanup_configuration in configuration.cleanup_configurations:
        cleanup_areas_proposals = {}

        for manager_type, prevent_delete_detectors in cleanup_configuration.cleanup_areas.items():
            # Need to use all credentials when cleaning up keys, as they can only be removed by the account that created
            # them
            credentials_to_use = [cleanup_configuration.credentials[0]] if manager_type != OpenstackKeypairManager \
                else cleanup_configuration.credentials

            all_area_delete_setups: List[DeleteSetup] = []
            all_area_marked_for_deletion: List[ItemAndReasons] = []
            all_area_not_marked_for_deletion: List[ItemAndReasons] = []

            for credentials in credentials_to_use:
                manager = manager_type(credentials)
                marked_for_deletion, not_marked_for_deletion = _create_area_report(
                    manager, prevent_delete_detectors, tracker)

                if not dry_run:
                    for item, _ in marked_for_deletion:
                        delete_setup: DeleteSetup = (item, lambda to_delete: manager.delete(item=to_delete))
                        all_area_delete_setups.append(delete_setup)
                all_area_marked_for_deletion += marked_for_deletion
                all_area_not_marked_for_deletion += not_marked_for_deletion

            cleanup_areas_proposals[manager_type] = all_area_delete_setups, all_area_marked_for_deletion, \
                                                    all_area_not_marked_for_deletion

        cleaup_proposal.append(cleanup_areas_proposals)

    return cleaup_proposal


def create_human_explaination(proposals) -> str:
    """
    TODO
    :param proposals: 
    :return: 
    """
    lines: List[str] = []
    for i in range(len(proposals)):
        lines.append(f"In cleanup configuration number {i +1}:")
        proposal = proposals[i]

        for manager_type, (delete_setups, marked_for_deletion, not_marked_for_deletion) in proposal.items():
            for item, reasons in marked_for_deletion:
                lines.append(f"Deleting item {create_human_identifier(item, True)} as not prevented: {reasons}")
            for item, reasons in not_marked_for_deletion:
                lines.append(f"Not deleting item {create_human_identifier(item, True)} as prevented: {reasons}")
            lines.append("")

        lines.append("")
        lines.append("")

    return "\n".join(lines)


def _create_area_report(manager: Manager, prevent_delete_detectors: Iterable[PreventDeleteDetector], tracker: Tracker) \
        -> Tuple[List[ItemAndReasons], List[ItemAndReasons]]:
    """
    TODO
    :param manager: 
    :param prevent_delete_detectors: 
    :param tracker: 
    :return: 
    """
    items = set(manager.get_all())
    registered = set(tracker.get_registered_identifiers(item_type=manager.item_type))

    new_items = items - registered
    tracker.register(new_items)

    old_items = registered - items
    tracker.unregister(old_items)

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
