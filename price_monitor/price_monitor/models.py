from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings
from datetime import datetime, date

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


class Listings(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_hash = Column(String(100), nullable=True)
    product_name = Column(String(100), nullable=False)
    product_url = Column(String(100), nullable=True)
    product_image_url = Column(String(200), nullable=True)
    price_excl = Column(Float, nullable=True)
    promo_flag = Column(String(20), nullable=True)
    retailer = Column(String(30), nullable=False)
    date_scraped = Column(DateTime, nullable=False, default=date.today())



