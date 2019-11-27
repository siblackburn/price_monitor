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
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import update


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
        self.listings.url_l3 = item['url_l3']
        self.listings.url_l2 = item['url_l2']
        self.listings.url_l1 = item['url_l1']

        query_unique = session.query(Listings).filter(Listings.date_scraped == date.today()).filter(
                Listings.product_name == self.listings.product_name).first()

        try:
            unique_check = query_unique
            print("MY EXISTING ENTRY: ", unique_check)

            if unique_check is None:
                print("ADDING TO DB")
                session.add(self.listings)
                session.commit()

            else:
                row = query_unique
                row.product_hash = item["product_id"]
                row.product_name = item['product_name']
                row.product_url = item['product_url']
                row.product_image_url = item['product_image']
                row.retailer = item['retailer_site']
                row.price_excl = item['price_excl']
                row.date_scraped = date.today()
                row.url_l3 = item['url_l3']
                row.url_l2 = item['url_l2']
                row.url_l1 = item['url_l1']

                # row.promo_flag = item['promo_flag']
                row.price_per_unit = item['price_per_unit']
                row.unit_of_measure = item['unit_measure']
                row.number_of_units = item['number_of_units']
                session.commit()
                print("UPDATED DB!!!!!!!!!!!1")

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