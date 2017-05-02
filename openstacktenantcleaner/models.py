from abc import ABCMeta
from datetime import datetime
from typing import NewType

from openstacktenantcleaner.external.hgicommon.models import Model

OpenstackIdentifier = NewType("OpenstackIdentifier", str)


class OpenstackCredentials(Model):
    """
    Credentials used to login to OpenStack.
    """
    def __init__(self, auth_url: str, tenant: str, username: str, password: str):
        """
        TODO
        :param auth_url: 
        :param username: 
        :param password: 
        """
        self.auth_url = auth_url
        self.tenant = tenant
        self.username = username
        self.password = password


class Timestamped(Model, metaclass=ABCMeta):
    """
    Timestamps.
    """
    def __init__(self, created_at: datetime=None, updated_at: datetime=None):
        self.created_at = created_at
        self.updated_at = updated_at


class OpenstackItem(Model, metaclass=ABCMeta):
    """
    An item in OpenStack.
    """
    def __init__(self, identifier: OpenstackIdentifier=None, name: str=None, **kwargs):
        super().__init__(**kwargs)
        self.identifier = identifier
        self.name = name


class OpenstackKeypair(OpenstackItem):
    """
    A key-pair in OpenStack.
    """
    def __init__(self, fingerprint: str=None, **kwargs):
        super().__init__(**kwargs)
        self.fingerprint = fingerprint


class OpenstackInstance(OpenstackItem, Timestamped):
    """
    An instance on OpenStack.
    """
    def __init__(self, image: str=None, key_name: str=None, **kwargs):
        super().__init__(**kwargs)
        self.image = image
        self.key_name = key_name


class OpenstackImage(OpenstackItem, Timestamped):
    """
    An image on OpenStack.
    """
    def __init__(self, protected: bool=None, **kwargs):
        super().__init__(**kwargs)
        self.protected = protected
