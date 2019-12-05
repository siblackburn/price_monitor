# -*- coding: utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class PriceMonitorItem(scrapy.Item):
    product_id = scrapy.Field()
    product_name = scrapy.Field()
    product_url = scrapy.Field()
    product_image = scrapy.Field()
    price_excl = scrapy.Field()
    retailer_site = scrapy.Field()
    promo_flag = scrapy.Field()
    promo_description = scrapy.Field()
    hidden_price = scrapy.Field()
    was_price = scrapy.Field()
    price_per_unit = scrapy.Field()
    unit_measure = scrapy.Field()
    number_of_units = scrapy.Field()
    url_l1 = scrapy.Field()
    url_l2 = scrapy.Field()
    url_l3 = scrapy.Field()
    cat_level1 = scrapy.Field()
    cat_level2 = scrapy.Field()
    cat_level3 = scrapy.Field()


class PriceMonitorStats(scrapy.Item):
    retailer = scrapy.Field()
    date_scraped = scrapy.Field()
    time_scraped = scrapy.Field()
    total_entries = scrapy.Field()
    total_fails = scrapy.Field()
    Total_crawl_time = scrapy.Field()

