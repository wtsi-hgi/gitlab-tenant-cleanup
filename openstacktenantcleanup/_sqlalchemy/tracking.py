from datetime import timedelta, datetime

from typing import Optional, Type, Collection

from openstacktenantcleanup._sqlalchemy._models import SqlAlchemyItemTracking, SqlAlchemyItem
from openstacktenantcleanup.external.sequencescape.database_connector import SQLAlchemyDatabaseConnector
from openstacktenantcleanup.models import OpenstackItem, OpenstackIdentifier
from openstacktenantcleanup.tracking import Tracker


class SqlTracker(Tracker):
    """
    SQL Tracker implementation.
    """
    def __init__(self, database_location: str):
        """
        Constructor.
        :param database_location: location of the SQL database 
        """
        self._database_connector = SQLAlchemyDatabaseConnector(database_location)

    def get_age(self, item: OpenstackItem) -> Optional[timedelta]:
        session = self._database_connector.create_session()
        tracking = session.query(SqlAlchemyItemTracking).get(item.identifier)
        session.close()
        if tracking is None:
            return None
        return datetime.now() - tracking.created

    def get_registered_identifiers(self, item_type: Optional[Type[OpenstackItem]]=None) -> Collection[OpenstackIdentifier]:
        type_filter = dict(type=item_type.__name__) if item_type is not None else {}
        session = self._database_connector.create_session()
        sql_alchemy_items = session.query(SqlAlchemyItem).filter_by(**type_filter).all()
        session.close()
        return [sql_alchemy_item.id for sql_alchemy_item in sql_alchemy_items]

    def _register(self, item: OpenstackItem, created: datetime):
        sql_alchemy_item = SqlAlchemyItem(id=item.identifier, type=type(item).__name__)
        sql_alchemy_item_tracking = SqlAlchemyItemTracking(id=item.identifier, created=created)
        session = self._database_connector.create_session()
        session.add(sql_alchemy_item)
        session.add(sql_alchemy_item_tracking)
        session.commit()
        session.close()

    def _unregister(self, item: OpenstackItem):
        session = self._database_connector.create_session()
        sql_alchemy_item = session.query(SqlAlchemyItem).filter_by(id=item.identifier).first()
        if sql_alchemy_item is not None:
            session.delete(sql_alchemy_item)
            session.commit()
        session.close()
