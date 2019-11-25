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
from scrapy.exporters import CsvItemExporter
from datetime import date
from .items import PriceMonitorItem, PriceMonitorCategories


class PriceMonitorPipeline(object):
    def __init__(self):
        self.file = open("test_scrape.csv", 'wb')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        if isinstance(item, PriceMonitorItem):
            self.exporter.export_item(item)
        return item

class PriceCrawlerDBPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()

        self.listings = Listings()
        # self.listings.product_hash = item["product_id"]
        self.listings.product_name = item['product_name']
        self.listings.product_url = item['product_url']
        self.listings.product_image_url = item['product_image']
        self.listings.retailer = item['retailer_site']
        self.listings.price_excl = item['price_excl']
        self.listings.date_scraped = date.today()

        # self.listings.promo_flag = item['promo_flag']

        try:
            existing_entry = session.query(Listings).filter(Listings.date_scraped == date.today()).filter(Listings.product_url == item['product_url']).first()
            if existing_entry is None:
                session.add(self.listings)
                session.commit()

        except:
            session.rollback()
            raise Exception(f'something went wrong')

        finally:
            session.close()

        return item


class CategorylinksPipeline(object):
    def __init__(self):
        self.file = open("category_links.csv", 'wb')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, cats, spider):
        if isinstance(cats, PriceMonitorCategories):
            self.exporter.export_item(cats)
        return cats