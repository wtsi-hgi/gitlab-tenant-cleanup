import os

from openstacktenantcleaner.models import OpenstackItem


def create_human_identifier(item: OpenstackItem, include_type: bool=False) -> str:
    """
    Creates a common, human readable message to allow the given item to be identified.
    :param item: the item
    :param include_type: whether to include the item's type in the message
    :return: the created message
    """
    type_message = f"of type \"{type(item).__name__}\" " if include_type else ""
    return f"{type_message}with id \"{item.identifier}\" and name \"{item.name}\""


def get_absolute_path_relative_to(path: str, relative_to: str) -> str:
    """
    Gets the path as relative to the given other path.
    :param path: path suffix
    :param relative_to: path prefix
    :return: the absolute path
    """
    if os.path.isabs(path):
        raise ValueError("The given path is not relative")
    return os.path.join(os.path.dirname(relative_to), path)
