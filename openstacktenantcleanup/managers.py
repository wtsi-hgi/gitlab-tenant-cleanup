from abc import ABCMeta, abstractmethod
from time import strptime

from dateutil.parser import parse as parse_datetime
from keystoneclient.v2_0.client import Client as KeystoneClient
from glanceclient.client import Client as GlanceClient
from novaclient.client import Client as NovaClient
from novaclient.exceptions import ClientException
from novaclient.v2.images import Image
from novaclient.v2.keypairs import Keypair
from novaclient.v2.servers import Server
from typing import TypeVar, Generic, Set, Iterable


from openstacktenantcleanup.models import OpenstackCredentials, OpenstackItem, OpenstackKeyPair, OpenstackInstance, \
    OpenstackImage, OpenstackIdentifier

Managed = TypeVar("Managed", bound=OpenstackItem)
RawModel = TypeVar("RawModel")


class Manager(Generic[Managed, RawModel], metaclass=ABCMeta):
    """
    Manager for OpenStack items.
    """
    # FIXME
    # @abstractmethod
    @property
    def item_type(self):
        """
        TODO
        :return: 
        """

    @abstractmethod
    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> RawModel:
        """
        Gets raw model of the OpenStack item with the given identifier.
        :param identifier: the OpenStack item's identifier
        :return: raw model of the OpenStack item
        """

    @abstractmethod
    def _get_all_raw(self) -> Iterable[RawModel]:
        """
        Gets raw models of all the OpenStack items of the type this manager manages.
        :return: all OpenStack items
        """

    @abstractmethod
    def _convert_raw(self, model: RawModel) -> Managed:
        """
        Converts the raw model to the domain model.
        :param model: the raw model
        :return: the domain model equivalent
        """

    @abstractmethod
    def _delete(self, item: Managed = None):
        """
        Deletes an OpenStack item with the given identifier.
        :param item: the OpenStack item to delete
        """

    def __init__(self, openstack_credentials: OpenstackCredentials):
        """
        Constructor.
        :param openstack_credentials: OpenStack credentials
        """
        self.openstack_credentials = openstack_credentials

    def get_by_id(self, identifier: OpenstackIdentifier=None) -> Managed:
        """
        Gets the managed OpenStack item that has the given identifier
        :param identifier: the item's identifier
        :return: the matched item
        """
        item = self._get_by_id_raw(identifier)
        return self._convert_raw(item)

    def get_all(self) -> Set[Managed]:
        """
        Gets all of the OpenStack items of the managed type.
        :return: the OpenStack items
        """
        models: Set[Managed] = set()
        for item in self._get_all_raw():
            models.add(self._convert_raw(item))
        return models

    def delete(self, *, item: Managed=None, identifier: OpenstackIdentifier=None):
        """
        Deletes the given OpenStack item.
        :param item: the item to delete 
        :param identifier: the identifier of the item to delete 
        """
        if item is not None and identifier is not None and item.identifier != identifier:
            raise ValueError(f"An item has been given with the identifier {item.identifier}, along with a different "
                             f"identifier {identifier} - provide either the item or the identifier")
        if item is None and identifier is None:
            raise ValueError("An item or identifier must be provided")
        if identifier is None and item is not None:
            identifier = item.identifier
        self._delete(identifier)


class _NovaManager(Generic[Managed, RawModel], Manager[Managed, RawModel], metaclass=ABCMeta):
    """
    Manager that uses Nova client.
    """
    NOVA_VERSION = "2"

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super().__init__(*args, **kwargs)
        self._client = NovaClient(_NovaManager.NOVA_VERSION, self.openstack_credentials.username,
                                  self.openstack_credentials.password, project_name=self.openstack_credentials.tenant,
                                  auth_url=self.openstack_credentials.auth_url)


class OpenstackKeyPairManager(_NovaManager[OpenstackKeyPair, Keypair]):
    """
    Manager for OpenStack key-pairs.
    """
    @property
    def item_type(self):
        return OpenstackKeyPair

    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> RawModel:
        return self._client.keypairs.get(identifier)

    def _get_all_raw(self) -> Iterable[RawModel]:
        return self._client.keypairs.list()

    def _convert_raw(self, model: Keypair) -> OpenstackKeyPair:
        return OpenstackKeyPair(
            identifier=model.name,
            name=model.name,
            fingerprint=model.fingerprint
        )

    def _delete(self, identifier: OpenstackIdentifier=None):
        self._client.keypairs.delete(identifier)

class OpenstackInstanceManager(_NovaManager[OpenstackInstance, Server]):
    """
    Manager for OpenStack instances.
    """
    @property
    def item_type(self):
        return OpenstackInstance

    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> RawModel:
        return self._client.servers.get(identifier)

    def _get_all_raw(self) -> Iterable[RawModel]:
        return self._client.servers.list()

    def _convert_raw(self, model: Server) -> OpenstackInstance:
        return OpenstackInstance(
            identifier=model.id,
            name=model.name,
            created_at=parse_datetime(model.created),
            updated_at=parse_datetime(model.updated),
            image=model.image["id"],
            key_name=model.key_name
        )

    def _delete(self, identifier: OpenstackIdentifier=None):
        try:
            self._client.servers.force_delete(identifier)
        except ClientException as e:
            if "nova.exception.InstanceInvalidState" not in e.message:
                raise e
            self._client.servers.reset_state(identifier)
            self._client.servers.force_delete(identifier)


class OpenstackImageManager(Manager[OpenstackImage, Image]):
    """
    Manager for OpenStack images.
    """
    GLANCE_VERSION = "2"

    @property
    def item_type(self):
        return OpenstackImage

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super().__init__(*args, **kwargs)
        keystone = KeystoneClient(
            auth_url=self.openstack_credentials.auth_url, username=self.openstack_credentials.username,
            password=self.openstack_credentials.password, tenant_name=self.openstack_credentials.tenant)
        glance_endpoint = keystone.service_catalog.url_for(service_type="image", endpoint_type="publicURL")
        self._client = GlanceClient(OpenstackImageManager.GLANCE_VERSION, glance_endpoint, token=keystone.auth_token)

    def _get_by_id_raw(self, identifier: OpenstackIdentifier = None) -> RawModel:
        return self._client.images.get(identifier)

    def _get_all_raw(self) -> Iterable[RawModel]:
        return self._client.images.list()

    def _convert_raw(self, model: Image) -> OpenstackImage:
        return OpenstackImage(
            identifier=model.id,
            name=model.name,
            created_at=parse_datetime(model.created_at),
            updated_at=parse_datetime(model.updated_at),
            protected=model.protected
        )

    def _delete(self, identifier: OpenstackIdentifier=None):
        self._client.images.delete(identifier)
