from abc import ABCMeta, abstractmethod
from datetime import timedelta, datetime

from typing import Optional, Type, Iterable, Union, Collection

from openstacktenantcleaner.models import OpenstackItem, Timestamped, OpenstackIdentifier


class Tracker(metaclass=ABCMeta):
    """
    Item age tracker.
    """
    @abstractmethod
    def get_age(self, item: OpenstackItem) -> Optional[timedelta]:
        """
        Gets the age of the given item on OpenStack.
        :param item: the item of interest
        :return: the item's age
        """

    @abstractmethod
    def _register(self, item: OpenstackItem, created: datetime):
        """
        Register the existence of an item with the given created time.
        :param item: the item that now exists 
        :param created: when the item was created
        """

    @abstractmethod
    def _unregister(self, item: Union[OpenstackItem, OpenstackIdentifier]):
        """
        Un-register the existence of an item.
        :param item: the item that no longer exists
        """

    @abstractmethod
    def get_registered_identifiers(self, item_type: Optional[Type[OpenstackItem]]=None) \
            -> Collection[OpenstackIdentifier]:
        """
        Gets identifiers of items that exist.
        :param item_type: the specific type of items to get
        :return: the registered items' identifiers
        """

    def register(self, item: Union[OpenstackItem, Iterable[OpenstackItem]]):
        """
        Register an item or items as having just come into existence.
        :param item: the item or items that have come into existence
        """
        items = [item] if isinstance(item, OpenstackItem) else item
        for item in items:
            if self.get_age(item) is None:
                created = item.created_at if isinstance(item, Timestamped) else datetime.now()
                self._register(item, created)

    def unregister(self, item: Union[OpenstackItem, Iterable[OpenstackItem], str, Iterable[str]]):
        """
        Un-register the existence of an item or items.
        :param item: the item or items that no longer exists
        """
        items = [item] if isinstance(item, OpenstackItem) or isinstance(item, str) else item
        for item in items:
            self._unregister(item)
