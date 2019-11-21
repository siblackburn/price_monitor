# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlparse
import urllib.parse
import csv
from scrapy.exporters import CsvItemExporter
import urljoin
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from price_monitor.items import PriceMonitorItem
import urllib3
import requests
import json
from bs4 import BeautifulSoup
import re


class DdcMonitorSpider(scrapy.Spider):
    name = 'ddc_monitor'
    allowed_domains = ['duluxdecoratorcentre.co.uk']
    start_urls = ['https://www.duluxdecoratorcentre.co.uk/']
    page_number = 0

    def __init__(self):
        self.declare_xpath()

    def declare_xpath(self):
        self.getAllCategoriesXpath = "/html/body/div[1]/header/div[1]/div/div[2]/div[3]/div/nav/ul/li/a/@href" #all category links by calling items in the list with href
        self.getAllSubCategoriesXpath = "/html/body/div[1]/header/div[1]/div/div[2]/div[3]/div/nav/ul/li/div/ul/li/div/a/@href" #all sub categories for aLL categories
        self.getAllMicroCategoriesXpath = "/html/body/div[1]/header/div[1]/div/div[2]/div[3]/div/nav/ul/li/div/ul/li/div/ul/li/a/@href" #all micro categories
        # at this point I'm now at a page with a list of products
        self.ProductLinksXpath = '//*[@id="list-of-products"]/li/div/div/div/div/a/@href'
        self.ProductNamesXpath = '//*[@id="list-of-products"]/li/div/div/div/div/a/span/text()' #product names in text
        self.ProductImagesXpath = '//*[@id="list-of-products"]/li/div/div/div/a/span/img' #Gives all details behind image. Will need to modify to just return the link/image file
        #Still need price data via a JS request:https://www.duluxdecoratorcentre.co.uk/productlist/postloadproductgroups

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
            url = response.urljoin(href.extract())+"?page=%d" % self.page_number


            yield scrapy.Request(url, callback=self.parse_main_item, dont_filter=True)


    def parse_main_item(self, response):
        item = PriceMonitorItem()
        scheme = DdcMonitorSpider.start_urls

        item['product_name'] = response.xpath(self.ProductNamesXpath).extract()
        item['product_url'] = response.xpath(self.ProductLinksXpath).extract()
        item['product_image'] = response.xpath(self.ProductImagesXpath).extract()
        yield item


