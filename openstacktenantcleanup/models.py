from abc import ABCMeta
from datetime import datetime

from openstacktenantcleanup.external.hgicommon.models import Model

OpenstackIdentifier = str


class OpenstackCredentials(Model):
    """
    TODO
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
    TODO
    """
    def __init__(self, created_at: datetime=None, updated_at: datetime=None):
        self.created_at = created_at
        self.updated_at = updated_at


class OpenstackItem(Model, metaclass=ABCMeta):
    """
    TODO
    """
    def __init__(self, identifier: OpenstackIdentifier=None, name: str=None, **kwargs):
        super().__init__(**kwargs)
        self.identifier = identifier
        self.name = name


class OpenstackKeyPair(OpenstackItem):
    """
    TODO
    """
    def __init__(self, fingerprint: str=None, **kwargs):
        super().__init__(**kwargs)
        self.fingerprint = fingerprint


class OpenstackInstance(OpenstackItem, Timestamped):
    """
    TODO
    """
    def __init__(self, image: str=None, key_name: str=None, **kwargs):
        super().__init__(**kwargs)
        self.image = image
        self.key_name = key_name


class OpenstackImage(OpenstackItem, Timestamped):
    """
    TODO
    """
    def __init__(self, protected: bool=None, **kwargs):
        super().__init__(**kwargs)
        self.protected = protected

