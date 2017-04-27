import enum

from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from openstacktenantcleanup.models import OpenstackItem

_item_types = {cls.__name__ for cls in OpenstackItem.__subclasses__()}
_item_types_dict = ({item_type: item_type for item_type in _item_types})
_OpenstackItemTypes = enum.Enum("OpenStackItemTypes", _item_types_dict)


SqlAlchemyModel = declarative_base()


class SqlAlchemyItem(SqlAlchemyModel):
    __tablename__ = "Item"
    id = Column(String, primary_key=True)
    type = Column(Enum(_OpenstackItemTypes))


class SqlAlchemyItemTracking(SqlAlchemyModel):
    __tablename__ = "ItemTracking"
    item = relationship(SqlAlchemyItem.__name__, single_parent=True, backref=backref(
        "tracking", cascade="all, delete-orphan"))
    id = Column(String, ForeignKey(f"{SqlAlchemyItem.__tablename__}.id"), primary_key=True)
    created = Column(DateTime)
