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

class WickesSpider(CrawlSpider):
    name = 'wickes_monitor'
    allowed_domains = ['wickes.co.uk']
    start_urls = ['https://www.wickes.co.uk']

    rules = Rule(LinkExtractor(allow='/Products/Decorating+Interiors/c/1000554'), callback='parse_main_item', follow=True),

    def parse_main_item(self, response):
        host = 'https://www.wickes.co.uk'
        url_l2 = str(response.url)
        url_l3 = response.xpath('/html/body/div/ul/li[last()-1]/a/@href').extract()
        url_l4 = response.xpath('/html/body/div/ul/li[last()-2]/a/@href').extract() #l4 doesn't tell you much (all painting and decorating. consider going one level deeper, like screwfix

        logging.info(f'attempting to scrape {url_l2} coming from {url_l3} > {url_l4}')

        ProductIDXpath = None# for wickes this is the number after the last forwardslash in the href
        ProductNamesXpath = '//*[contains(@id, "product_item")]/a/@title' # for WICKES
        ProductLinksXpath = '//*[contains(@id, "product_item")]/a/@href'  # all product links: WICKES
        ProductImagesXpath = '//*[contains(@id, "product_item")]/a/img/@src'  # for WICKES
        PriceincXpath = '//*[contains(@id, "product_item")]/div/div[2]/div[2]/text()' #wickes. need to remove no numerics, divide for vat, and take 10% off for trade price
        PricePerUnitXpath = '//*[contains(@id, "product_item")]/div/div[2]/div[3]/text()' # WICKES need to remove non numerics, but could also extract unit measure (e.g. per L)
        WasPRiceXpath = '//*[contains(@id, "product_item")]/div/div[2]/div[1]/s/text()' #WICKES: UNUSED, but could be used
        PromoOfferXpath = '//*[contains(@id, "product_item")]/div[1]/div/text()' # need a regex expression to remove \n, \t

        Url_l2NameXpath = 'normalize-space(/html/body/main/div[2]/div[1]/h1/text())'
        Url_l3NameXpath = '/html/body/div/ul/li[last()-1]/a/span/text()'
        Url_l4NameXpath = '/html/body/div/ul/li[last()-2]/a/span/text()'

        for product in zip(
            response.xpath(ProductIDXpath).extract(),
            response.xpath(ProductNamesXpath).extract(),
            response.xpath(ProductLinksXpath).extract(),
            response.xpath(ProductImagesXpath).extract(),
            response.xpath(PriceincXpath).extract(),
            response.xpath(PricePerUnitXpath).extract(),
            response.xpath(Url_l2NameXpath).extract(),
            response.xpath(Url_l3NameXpath).extract(),
            response.xpath(Url_l4NameXpath).extract(),

        ):
            price_formatted = re.sub("[^\d\.]", "", product[4])
            price_excl = round(float(price_formatted) / 1.2, 2)
            trade_price_excl = round(price_excl * 0.9, 2)

            price_per_unit = re.sub("[^\d\.]", "", product[5])
            price_perunit_formatted = round(float(price_per_unit), 2)

            unit_measure_reg = re.compile(r'\bper.*\b')

            logging.info(f'There are {len(product)} products found')

            item = PriceMonitorItem()
            item['product_id'] = product[0]
            item['product_name'] = product[1]
            item['product_url'] = product[2]
            item['product_image'] = product[3]
            item['price_excl'] = trade_price_excl
            item['retailer_site'] = host
            item['price_per_unit'] = price_perunit_formatted
            item['unit_measure'] = unit_measure_reg.findall(product[5])
            item['number_of_units'] = float(round((item['price_excl'] / item['price_per_unit']), 3))
            item['url_l4'] = url_l4
            item['url_l3'] = url_l3
            item['url_l2'] = url_l2
            item['url_l4_name'] = product[8]
            item['url_l3_name'] = product[7]
            item['url_l2_name'] = product[6]

            if (item['product_name'] or item['price_excl'] or item['retailer'] or item['product_url']) is None:
                logging.info(f'item returned no info: {response.url}')

            yield item

