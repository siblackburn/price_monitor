# -*- coding: utf-8 -*-
import scrapy
import logging
from urllib.parse import urlparse
import urllib.parse
from scrapy.exporters import CsvItemExporter
import urljoin
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from price_monitor.items import PriceMonitorItem
from scrapy.linkextractors import LinkExtractor
import re

class ScrewfixSpider(CrawlSpider):
    name = 'sf_monitor'
    allowed_domains = ['screwfix.com']
    start_urls = ['https://www.screwfix.com/c/decorating/cat850130']

    rules = Rule(LinkExtractor(allow='/c/decorating'), callback='parse_main_item', follow=True),

    def parse_main_item(self, response):
        host = 'https://www.screwfix.com'
        url_l2 = str(response.url)
        url_l1 = response.xpath('//*[@id="breadcrumb_item_search_result_2_top"]/@href').extract()
        # url_l4 = response.xpath('//*[@id="breadcrumb_item_search_result_1_top"]/@href').extract()

        logging.info(f'attempting to scrape {url_l2} coming from {url_l1}')

        ProductIDXpath = '//*[contains(@id, "product_quote")]/@quotenumberproductid' #for SF
        ProductNamesXpath = '//*[contains(@id, "product_description")]/@title'  # for SF
        ProductLinksXpath = '//*[contains(@id, "product_description")]/@href'  # all product links: SF
        ProductImagesXpath = '//*[contains(@id, "product_image")]/@src'  # for SF
        PriceincXpath = '//*[contains(@id, "product_list_price")]/text()' #for SF. Is inc vat, and with a £ sign
        PromoOfferXpath = '//*[contains(@id, "productID")]/div[3]/div/div/div/span/text()' #does NOT return the list in correct order. Might need to lookup product ID in same part of Dom to match with productid above
        WasPriceXpath = '//*[contains(@id, "addToTrolleyForm")]/div/div[1]/div[2]/span[1]/text()' #Same as promo offer...might need to lookup product id to get this in the right order

        for product in zip(
            response.xpath(ProductIDXpath).extract(),
            response.xpath(ProductNamesXpath).extract(),
            response.xpath(ProductLinksXpath).extract(),
            response.xpath(ProductImagesXpath).extract(),
            response.xpath(PriceincXpath).extract(),

        ):
            price_formatted = re.sub("[^\d\.]", "", product[4])
            price_excl = round(float(price_formatted) / 1.2, 2)

            logging.info(f'There are {len(product)} products found')

            item = PriceMonitorItem()
            item['product_id'] = product[0]
            item['product_name'] = product[1]
            item['product_url'] = product[2]
            item['product_image'] = product[3]
            item['price_excl'] = price_excl
            item['retailer_site'] = host
            item['price_per_unit'] = None
            item['unit_measure'] = None
            item['number_of_units'] = None
            item['url_l3'] = None
            item['url_l2'] = url_l2
            item['url_l1'] = url_l1
            item['cat_level3'] = None
            item['cat_level2'] = None
            item['cat_level1'] = None
            item['was_price'] = None
            item['promo_description'] = None

            if (item['product_name'] or item['price_excl'] or item['retailer'] or item['product_url']) is None:
                logging.info(f'item returned no info: {response.url}')

            yield item

