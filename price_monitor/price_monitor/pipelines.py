# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from price_monitor.models import Listings, Scrape_Stats, db_connect, create_table
from sqlalchemy.orm import sessionmaker
from scrapy.exporters import CsvItemExporter
from datetime import date
from .items import PriceMonitorItem, PriceMonitorStats
from sqlalchemy.dialects.mysql import insert
import logging

logger = logging.getLogger('customizedlogger')

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
        self.listings.product_hash = item["product_id"]
        self.listings.product_name = item['product_name']
        self.listings.product_url = item['product_url']
        self.listings.product_image_url = item['product_image']
        self.listings.retailer = item['retailer_site']
        self.listings.price_excl = item['price_excl']
        self.listings.date_scraped = date.today()

        # self.listings.promo_flag = item['promo_flag']
        self.listings.price_per_unit = item['price_per_unit']
        self.listings.unit_of_measure = item['unit_measure']
        self.listings.number_of_units = item['number_of_units']
        self.listings.url_l4 = item['url_l4']
        self.listings.url_l3 = item['url_l3']
        self.listings.url_l2 = item['url_l2']

        columns_to_dict = lambda obj: {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

        try:
            insert_stmt = insert(Listings).values(
                **columns_to_dict(self.listings))

            on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                {'product_name': self.listings.product_name, 'date_scraped': date.today(), 'retailer': self.listings.retailer}
            )

            logging.info(f'attempting to write db entry: {self.listings.product_name} on date {self.listings.date_scraped}')
            session.execute(on_duplicate_key_stmt)
            logging.info(f'Executed duplicate key statement')
            session.commit()

        except:
            session.rollback()
            logging.info(f'item was not written to database: {self.listings.product_name}, {self.listings.product_url}, {self.listings.url_l2}, {self.listings.url_l3}')
            raise Exception(f'something went wrong')

        finally:
            session.close()

        return item


class PriceCrawlerStatsPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()

        self.listings = ScrapeStats()


# class CategorylinksPipeline(object):
#     def __init__(self):
#         self.file = open("category_links.csv", 'wb')
#         self.exporter = CsvItemExporter(self.file)
#         self.exporter.start_exporting()
#
#     def close_spider(self, spider):
#         self.exporter.finish_exporting()
#         self.file.close()
#
#     def process_item(self, cats, spider):
#         if isinstance(cats, PriceMonitorCategories):
#             self.exporter.export_item(cats)
#         return cats