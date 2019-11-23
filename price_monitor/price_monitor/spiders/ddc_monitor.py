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
from price_monitor.items import PriceMonitorItem
from scrapy.http import FormRequest
import re


class DdcMonitorSpider(scrapy.Spider):
    name = 'ddc_monitor'
    allowed_domains = ['duluxdecoratorcentre.co.uk']
    start_urls = ['https://www.duluxdecoratorcentre.co.uk/']
    page_number = 1

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

        self.PageNotFoundXpath = 'normalize-space(//*[@id="productListPage"]/div/text())'

        self.price_IDXpath = '//*[@id="list-of-products"]/li/@data-id'


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

            page = 1
            # if response.xpath(self.PageNotFoundXpath).extract() != 'No products found.':
            while page < 2:
                next_page = url+"?page=%d" % page
                page += 1
                print(next_page)
                yield scrapy.Request(next_page, callback=self.parse_main_item, dont_filter=True)

            yield scrapy.Request(url, callback=self.parse_main_item, dont_filter=True)


    def parse_main_item(self, response):
        scheme = DdcMonitorSpider.start_urls

        # there are multiple products per page, so we should generate a list of products right?
        items_by_id = {}
        for product in zip(
            response.xpath(self.price_IDXpath).extract(),
            response.xpath(self.ProductNamesXpath).extract(),
            response.xpath(self.ProductLinksXpath).extract(),
            response.xpath(self.ProductImagesXpath).extract()
        ):
            item = PriceMonitorItem()
            item['product_id'] = product[0]
            item['product_name'] = product[1]
            item['product_url'] = product[2]
            item['product_image'] = product[3]

            # set item into our dictionary by id
            items_by_id[product[0]] = item
        
        def form_callback(response):

            # populate the price information of each item and then return our items
            for price_info in json.loads(response.text):
                product_id = price_info['Id']
                price = price_info['PriceInclVat']
                if product_id in items_by_id:
                    items_by_id[product_id]['price_excl'] = price

            # return all the items found
            for item in items_by_id.values():
                yield item


        # use FormRequest to do a proper form post (source: https://docs.scrapy.org/en/latest/topics/request-response.html#using-formrequest-to-send-data-via-http-post)
        post_url = "https://www.duluxdecoratorcentre.co.uk/productlist/postloadproductgroups"
        yield FormRequest(post_url,
            formdata=dict(ids=list(items_by_id.keys())),
            callback=form_callback
        )

    # def pagination(self, response):
    #     pagination_test = response.xpath(self.PageNotFoundXpath).extract()
    #     yield scrapy.Request(pagination_test, callback=self.parse_subcategory(), dont_filter=True)


