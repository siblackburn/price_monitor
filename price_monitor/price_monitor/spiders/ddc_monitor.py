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
    start_urls = ['https://www.duluxdecoratorcentre.co.uk']

    def __init__(self):
        self.declare_xpath()

    def declare_xpath(self):
        self.getAllCategoriesXpath = "/html/body/div[1]/header/div[1]/div/div[2]/div[3]/div/nav/ul/li/a/@href" #all category links by calling items in the list with href
        self.getAllSubCategoriesXpath = "/html/body/div[1]/header/div[1]/div/div[2]/div[3]/div/nav/ul/li/div/ul/li/div/a/@href" #all sub categories for aLL categories
        self.getAllMicroCategoriesXpath = "/html/body/div[1]/header/div[1]/div/div[2]/div[3]/div/nav/ul/li/div/ul/li/div/ul/li/a/@href" #all micro categories
        # at this point I'm now at a page with a list of products
        self.ProductLinksXpath = '//*[@id="list-of-products"]/li/div/div/div/div/a/@href'
        self.ProductNamesXpath = '//*[@id="list-of-products"]/li/div/div/div/div/a/span/text()' #product names in text
        self.ProductImagesXpath = '//*[@id="list-of-products"]/li/div/div/div/a/span/img/@alt' #Gives all details behind image. Will need to modify to just return the link/image file
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
                yield scrapy.Request(next_page, callback=self.parse_main_item, dont_filter=True)

            yield scrapy.Request(url, callback=self.parse_main_item, dont_filter=True)
            # yield scrapy.Request(url="https://www.duluxdecoratorcentre.co.uk/special-offers", callback=self.parse_main_item, dont_filter=True)
            # Need to also add a separate yield for the special offers page, which doesn't have sub category links and so doesn't get passed to main parse

    def parse_main_item(self, response):
        scheme = DdcMonitorSpider.start_urls

        # NOTE(yuri): there are multiple products per page, so we should generate a list of products right?
        # I create a dictionary of items by their product ID. I do this because when I fetch the price information
        # later, I will need to match up the price with the proper product ID.
        items_by_id = {}
        for product in zip(
            response.xpath(self.price_IDXpath).extract(),
            response.xpath(self.ProductNamesXpath).extract(),
            response.xpath(self.ProductLinksXpath).extract(),
            response.xpath(self.ProductImagesXpath).extract(),
            self.start_urls
        ):
            item = PriceMonitorItem()
            item['product_id'] = product[0]
            item['product_name'] = product[1]
            item['product_url'] = product[2]
            item['product_image'] = product[3]
            item['retailer_site'] = product[4]

            # set item into our dictionary by id
            items_by_id[product[0]] = item
        
        # this function is called after the price information has been fetched
        def price_form_callback(response):
            # populate the price information of each item and then return our items
            for price_info in json.loads(response.text):
                product_id = price_info['Id']
                price = price_info['PriceExclVat']
                price_formatted = price[1:]

                # lookup the product by id and update it's price field
                if product_id in items_by_id:
                    items_by_id[product_id]['price_excl'] = float(price_formatted)

            # return all the items found
            for items in items_by_id.values():
                yield items

        # use FormRequest to do a proper form post (source: https://docs.scrapy.org/en/latest/topics/request-response.html#using-formrequest-to-send-data-via-http-post)
        post_url = "https://www.duluxdecoratorcentre.co.uk/productlist/postloadproductgroups"
        yield FormRequest(post_url,
            formdata=dict(ids=list(items_by_id.keys())),
            callback=price_form_callback
                                        )

        '''
        Pulling promo flag from the promo Javascript post request
        '''
        # def promo_form_callback(res):
        #     for promo_info in json.loads(res.text):
        #         product_id = promo_info['Id']
        #         promo = promo_info['Promotions']
        #         if promo > 0:
        #             promo_flag = "promo"
        #         else:
        #             promo_flag = "no promo"
        #
        #         # lookup the product by id and update promo flag
        #         if product_id in items_by_id:
        #             items_by_id[product_id]['promo_flag'] = promo_flag
        #
        #     for promo_f in items_by_id.values():
        #         yield promo_f
        #
        # promo_url = "https://www.duluxdecoratorcentre.co.uk/productlist/getlistpromotions"
        # yield FormRequest(promo_url,
        #                   formdata=dict(ids=list(items_by_id.keys())),
        #                   callback=promo_form_callback
        #                   )




