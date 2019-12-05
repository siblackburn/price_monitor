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
    start_urls = ['https://www.wickes.co.uk/Products/Decorating+Interiors/c/1000554']
    rules = Rule(LinkExtractor(allow='(Decorating)'),
                               callback='parse_main_item', follow=True),

    def parse_main_item(self, response):
        host = 'https://www.wickes.co.uk'
        url_l3 = str(response.url)
        url_l2 = str(response.xpath('/html/body/div/ul/li[last()-1]/a/@href').extract())
        url_l1 = str(response.xpath('/html/body/div/ul/li[last()-2]/a/@href').extract()) #l4 doesn't tell you much (all painting and decorating. consider going one level deeper, like screwfix
        logging.info(f'attempting to scrape {url_l3} coming from {url_l2} > {url_l1}')

        # ProductIDXpath = None# for wickes this is the number after the last forwardslash in the href
        ProductNamesXpath = '//*[contains(@id, "product_item")]/a/@title' # for WICKES
        ProductLinksXpath = '//*[contains(@id, "product_item")]/a/@href'  # all product links: WICKES
        ProductImagesXpath = '//*[contains(@id, "product_item")]/a/img/@src'  # for WICKES
        PriceincXpath = '//*[contains(@id, "product_item")]/div/div[2]/div[2]/text()' #wickes. need to remove no numerics, divide for vat, and take 10% off for trade price
        PricePerUnitXpath = '//*[contains(@id, "product_item")]/div/div[2]/div[3]/text()' # WICKES need to remove non numerics, but could also extract unit measure (e.g. per L)
        WasPRiceXpath = '//*[contains(@id, "product_item")]/div/div[2]/div[1]/s/text()' #WICKES: UNUSED, but could be used
        PromoDescriptionXpath = '//*[contains(@id, "product_item")]/div[1]/div/text()' # need a regex expression to remove \n, \t. This doesn't necessariyl come out in the same order as products, would need to check

        cat_level3Xpath = 'normalize-space(/html/body/main/div[2]/div[1]/h1/text())'
        cat_level2Xpath = '/html/body/div/ul/li[last()-1]/a/span/text()'
        cat_level1Xpath = '/html/body/div/ul/li[last()-2]/a/span/text()'

        for product in zip(
            response.xpath(ProductNamesXpath).extract(),
            response.xpath(ProductLinksXpath).extract(),
            response.xpath(ProductImagesXpath).extract(),
            response.xpath(PriceincXpath).extract(),
            response.xpath(PricePerUnitXpath).extract(),
            response.xpath(cat_level3Xpath).extract(),
            response.xpath(cat_level2Xpath).extract(),
            response.xpath(cat_level1Xpath).extract(),
            response.xpath(WasPRiceXpath).extract(),
            response.xpath(PromoDescriptionXpath).extract(),

        ):
            #format the price, by removing evertthing but numbers and decimal
            price_formatted = re.sub("[^\d\.]", "", product[3])
            #turn into excluding vat
            price_excl = round(float(price_formatted) / 1.2, 2)
            trade_price_excl = round(price_excl * 0.9, 2)

            #format the price per unit measure (the numerical element) and backcalculate number of units in product
            price_per_unit = re.sub("\[p].*$|[^\d\.]", "", product[4])
            price_per_unit = price_per_unit[0:5]
            if price_per_unit.replace('.', '', 1).isdigit():
                price_per_unit_formatted = float(price_per_unit)
                number_of_units = (price_excl * 1.2) / price_per_unit_formatted
            else:
                price_per_unit_formatted = None
                number_of_units = None

            unit_measure_reg = re.compile(r'\bper.*\b')
            unit_measure = unit_measure_reg.findall(product[4])
            promo_description = product[9].strip()
            was_price = re.sub("[^\d\.]", "", product[8]).strip()

            logging.info(f'There are {len(product)} products found')

            item = PriceMonitorItem()
            item['product_name'] = product[0]
            item['product_url'] = host + product[1]
            item['product_image'] = product[2]
            item['price_excl'] = trade_price_excl
            item['retailer_site'] = host
            item['price_per_unit'] = price_per_unit_formatted
            item['unit_measure'] = unit_measure
            item['number_of_units'] = number_of_units
            item['url_l3'] = url_l3
            item['url_l2'] = url_l2
            item['url_l1'] = url_l1
            item['cat_level3'] = None
            item['cat_level2'] = product[5]
            item['cat_level1'] = product[6]
            item['product_id'] = None
            item['was_price'] = float(was_price) # need to strop \n before enabling this. Same problem as promo description, where normalize space would not return a value
            item['promo_description'] = promo_description if str else None

            logging.info(f'there are {len(item)} items in item')

            if (item['product_name'] or item['price_excl'] or item['retailer'] or item['product_url']) is None:
                logging.info(f'item returned no info: {response.url}')

            yield item

