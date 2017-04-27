from openstacktenantcleanup.models import OpenstackItem


def create_human_identifier(item: OpenstackItem, include_type: bool=False) -> str:
    """
    Creates a common, human readable message to allow the given item to be identified.
    :param item: the item
    :param include_type: whether to include the item's type in the message
    :return: the created message
    """
    type_message = f"of type \"{type(item).__name__}\" " if include_type else ""
    return f"{type_message}with id \"{item.identifier}\" and name \"{item.name}\""
