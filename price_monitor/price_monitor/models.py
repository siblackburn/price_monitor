from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings
from datetime import datetime, date, timezone
from sqlalchemy import UniqueConstraint
import pytz

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(bind=engine)


class Listings(Base):
    __tablename__ = "listings"

    unique_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False) # required
    product_hash = Column(String(200), nullable=True)
    product_name = Column(String(200), nullable=False) # required
    product_url = Column(String(200), nullable=False) # required
    product_image_url = Column(String(300), nullable=True)
    price_excl = Column(Float, nullable=False) # required
    promo_flag = Column(String(20), nullable=True)
    promo_description = Column(String(200), nullable=True)
    hidden_price = Column(Float, nullable=True)
    was_price = Column(Float, nullable=True)
    retailer = Column(String(300), nullable=False)  # required
    date_scraped = Column(DateTime, nullable=False, default=date.today())
    price_per_unit = Column(Float, nullable=True)
    unit_of_measure = Column(String(10), nullable=True)
    number_of_units = Column(Float, nullable=True)
    url_l1 = Column(String(300), nullable=True)
    url_l2 = Column(String(300), nullable=True)
    url_l3 = Column(String(300), nullable=True)
    cat_level1 = Column(String(300), nullable=True)
    cat_level2 = Column(String(300), nullable=True)
    cat_level3 = Column(String(300), nullable=True)

    UniqueConstraint('date_scraped', 'product_url', 'retailer', name='date_product_retailer_unique_constraint')


class ScrapeStats(Base):
    __tablename__ = "scrape_stats"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # retailer = Column(String(100), nullable=True) #need to change foreign key to table containing retailer, once the table is created
    # date_scraped = Column(DateTime, nullable=False, default=date.today())
    # time_scraped = Column(Date, nullable=False, default=pytz.timezone('GMT'))
    total_entries = Column(Integer, nullable=True)
    # total_fails = Column(Integer, nullable=True)
    # Total_crawl_time = Column(DateTime, nullable=True)









