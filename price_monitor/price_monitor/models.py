from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings
from datetime import datetime, date
from sqlalchemy.ext.hybrid import hybrid_property

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

    unique_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_hash = Column(String(200), nullable=True)
    product_name = Column(String(200), nullable=False)
    product_url = Column(String(200), nullable=True)
    product_image_url = Column(String(200), nullable=True)
    price_excl = Column(Float, nullable=True)
    promo_flag = Column(String(20), nullable=True)
    retailer = Column(String(300), nullable=False)
    date_scraped = Column(DateTime, nullable=False, default=date.today())

    # insert column to check if scraped data is already in database
    # consider either hybried_property or column_property

    @hybrid_property
    def url_date(self):
        return self.product_url + self.date_scraped






