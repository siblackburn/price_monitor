# -*- coding: utf-8 -*-
import scrapy
import logging
from urllib.parse import urlparse
import urllib.parse
import json
import csv
from scrapy.exporters import CsvItemExporter
import urljoin
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from price_monitor.items import PriceMonitorItem, PriceMonitorCategories
from scrapy.http import FormRequest
import re


class TradePointSpider(scrapy.Spider):
    name = 'tradepoint_monitor'
    allowed_domains = ['trade-point.co.uk']
    start_urls = ['https://www.trade-point.co.uk/']

    def __init__(self):
        self.declare_xpath()

    def declare_xpath(self):
        self.getAllCategoriesXpath = '//*[@id="site-nav"]/div/ul/li[6]/div/div/div/div/a/@href'  # TP categry links > yo return painting and decorating href. e.g. paint
        self.getAllSubCategoriesXpath = '//*[@id="content"]/div/div/div[2]/div[1]/div/section[1]/div/ul/li/div/article/div/div/h3/a/@href'  # TP all sub categories, e.g.interior emulsion
        self.getAllMicroCategoriesXpath = '//*[@id="content"]/div/div/div[2]/div[1]/div/section[1]/div/ul/li/div/article/div/div/h3/a/@href' #each TP micro cat - e.g. bathroom paint
        self.getALLPagesXpath = '//*[@id="ui-jump-hook"]/ul/li/a/@href' #return all paginated pages (e.g. page=4)

        self.ProductLinksXpath = '//*[@id]/div/div/h3/a/@href' # all product links: TP
        self.ProductNamesXpath = '//*[@id]/div/div/h3/a/text()'  # product names in text: TP
        self.ProductImagesXpath = '//*[@id]/a/img'  #link to TP images
        self.PricePoundsXpath = '//*[@id]/div[1]/div[2]/div/p[2]/strong/span/span[2]/text()'
        self.PricePenceXpath = '//*[@id]/div[1]/div[2]/div/p[2]/strong/span/span[4]/text()'

    def parse(self, response):
        for href in response.xpath(self.getAllCategoriesXpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        for href in response.xpath(self.getAllSubCategoriesXpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_subcategory)

    def parse_subcategory(self, response):
        for href in response.xpath(self.getAllMicroCategoriesXpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_microcategory, dont_filter=True)

    def parse_microcategory(self, response):
        for href in response.xpath(self.getALLPagesXpath):
            url = response.urljoin(href.extract())

            #test to see what category links are being crawled. Main crawler is not returning as many products as expected
            cats = PriceMonitorCategories()
            cats['category_link'] = url
            yield cats

            yield scrapy.Request(url, callback=self.parse_main_item, dont_filter=True)

    def parse_main_item(self, response):
        for product in zip(
            response.xpath(self.ProductNamesXpath).extract(),
            response.xpath(self.ProductLinksXpath).extract(),
            response.xpath(self.ProductImagesXpath).extract(),
            response.xpath(self.PricePoundsXpath).extract(),
            response.xpath(self.PricePenceXpath).extract(),
            self.start_urls
        ):
            item = PriceMonitorItem()
            item['product_name'] = product[0]
            item['product_url'] = product[1]
            item['product_image'] = product[2]
            item['price_excl'] = float(product[3] + "." + product[4])
            item['retailer_site'] = product[5]

            yield item






