import sqlalchemy

from sqlalchemy import (Column, Date, DateTime, Float, ForeignKey, Index,
                        Integer, String, Table, desc)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .access import get_engine, get_session

Base = declarative_base()


def setup_database(echo=False, drop=True):
    """Setup the database, dropping any existing tables by default."""
    engine = get_engine(echo=echo)
    session = get_session(echo=echo)
    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

# http://docs.sqlalchemy.org/en/latest/_modules/examples/graphs/directed_graph.html

# Manual relationship

# stores_items = Table('stores_items', Base.metadata,
#                      Column('transaction_number', String, primary_key=True,
#                             index=True),
#                      Column('store_number', Integer, ForeignKey('Store.number'),
#                             index=True),
#                      Column('item_number', Integer, ForeignKey('Item.number'),
#                             index=True)
#                      )

# http://docs.sqlalchemy.org/en/latest/_modules/examples/graphs/directed_graph.html

class Page(Base):
    __tablename__ = "Page"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    # text = Column(String)
    last_modified = Column(DateTime)

    categories = relationship("Link", back_populates="pages")


    # items = relationship("Item", secondary=stores_items,
    #                      back_populates="stores")

    # __mapper_args__ = {
    #     "order_by": [county_number, zip_code]
    # }

class Category(Base):
    __tablename__ = "Category"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    pages = relationship("Page", back_populates="categories")

# class Link(Base):
#     __tablename__ = "Link"
#

# class CategoryLink(Base):
#     __tablename__ = "Category"
#     id = Column(Integer, primary_key=True)
#     pages = relationship("Link", back_populates="source")