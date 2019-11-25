# -*- coding: utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy

class PriceMonitorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # need to declare fields before assigning them
    product_id = scrapy.Field()
    product_name = scrapy.Field()
    product_url = scrapy.Field()
    product_image = scrapy.Field()
    price_excl = scrapy.Field()
    retailer_site = scrapy.Field()
    promo_flag = scrapy.Field()


class PriceMonitorCategories(scrapy.Item):
    category_link = scrapy.Field()