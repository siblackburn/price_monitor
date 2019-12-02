# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from price_monitor.models import Listings, ScrapeStats, db_connect, create_table
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
            logging.info(f'{self.listings.product_name} committed to DB')

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

    def process_item(self, total_entries, spider):
        session = self.Session()

        self.scrape_stats = ScrapeStats()
        self.scrape_stats.total_entries = total_entries

        columns_to_dict = lambda obj: {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

        try:
            insert_stmt = insert(Listings).values(
                **columns_to_dict(self.scrape_stats))

            on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                {'date_scraped': date.today(), 'time_scraped': self.scrape_stats.time_Scraped, 'retailer': self.scrape_stats.retailer}
            )

            logging.info(f'attempting to write db entry: {self.scrape_stats.retailer} on date {self.scrape_stats.date_scraped}')
            session.execute(on_duplicate_key_stmt)
            logging.info(f'Executed duplicate key statement')
            session.commit()
            logging.info(f'{self.scrape_stats.retailer} committed to DB')

        except:
            session.rollback()
            logging.info(f'item was not written to database:{self.scrape_stats.retailer} on date {self.scrape_stats.date_scraped}')
            raise Exception(f'something went wrong')

        finally:
            session.close()

        return total_entries


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