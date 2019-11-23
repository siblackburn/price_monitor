# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from price_monitor.models import Listings, db_connect, create_table
from sqlalchemy.orm import sessionmaker
import db


class PriceMonitorPipeline(object):
    def process_item(self, item, spider):
        return item

class PriceCrawlerDBPipeline(object):
    def __init__(self):
        engine = db.connect()
        create_engine(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()

        listings = Listings()
        listings.product_hash = item["product_id"]
        listings.product_name = item['product_name']
        listings.product_url = item['product_url']
        listings.product_image_url = item['product_image']
        listings.retailer = item['retailer_site']
        listings.price_excl = item['price_excl']
        listings.promo_flag = item['promo_flag']

        try:
            session.add(listings)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item
