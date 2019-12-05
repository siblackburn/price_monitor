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
from scrapy.extensions import closespider
from scrapy.statscollectors import StatsCollector

class DdcMonitorSpider(scrapy.Spider):
    name = 'ddc_monitor'
    allowed_domains = ['duluxdecoratorcentre.co.uk']
    start_urls = ['https://www.duluxdecoratorcentre.co.uk']


    def __init__(self):
        self.declare_xpath()

    def declare_xpath(self):
        self.getAllCategoriesXpath = "/html/body/div[1]/header/div[1]/div/div[2]/div[3]/div/nav/ul/li/a/@href"  # all category links by calling items in the list with href
        self.getAllPaintsubcatsXpath = '//*[@id="flexiPage"]/div/div/div/div/div/div/div/div/div/div/div/a/@href'  # all sub categories for aLL categories
        self.getAllWoodsubcatsXpath = '//*[@id="flexiPage"]/div/div/div/div/div/a/@href'
        self.getAllAccessoriesXpath = '//*[@id="flexiPage"]/div/div/div/div/div/div/div/a/@href'
        self.getAllWallpapersXpath = '//*[@id="flexiPage"]/div[1]/div/div/div/ul/li/a/@href'
        # self.getAllMicroCategoriesXpath = "/html/body/div[1]/header/div[1]/div/div[2]/div[3]/div/nav/ul/li/div/ul/li/div/ul/li/a/@href" #all micro categories

        self.GetProductCountXpath = 'normalize-space(//*[@id="product-list-panel"]/div[1]/div[1]/text())'
        self.ProductLinksXpath = '//*[@id="list-of-products"]/li/div/div/div/div/a/@href'
        self.ProductNamesXpath = '//*[@id="list-of-products"]/li/div/div/div/div/a/span/text()'  # product names in text
        self.ProductImagesXpath = '//*[@id="list-of-products"]/li/div/div/div/a/span/img/@alt'  # Gives all details behind image. Will need to modify to just return the link/image file
        # Still need price data via a JS request:https://www.duluxdecoratorcentre.co.uk/productlist/postloadproductgroups
        self.PageNotFoundXpath = 'normalize-space(//*[@id="productListPage"]/div/text())'
        self.price_IDXpath = '//*[@id="list-of-products"]/li/@data-id'
        self.catlevel3Xpath ='/html/body/div[1]/div[3]/div/div[1]/div/ul/li[4]/a/text()' #once on a page with products
        self.catlevel2Xpath = '/html/body/div[1]/div[3]/div/div[1]/div/ul/li[3]/a/text()'
        self.catlevel1Xpath = '/html/body/div[1]/div[3]/div/div[1]/div/ul/li[2]/a/text()'

    def parse(self, response):
        for href in response.xpath(self.getAllCategoriesXpath):
            url = response.urljoin(href.extract())  # returns something like duluxdecoratorcentre.co.uk/products/paint
            yield scrapy.Request(url=url, callback=self.parse_category, meta={'url_l1': str(url)}, )

    def parse_category(self, response):
        for href in response.xpath(self.getAllPaintsubcatsXpath):
            url = response.urljoin(href.extract())
            url_l1 = response.meta.get('url_l1')
            logging.info(f'url_l1 is {url_l1} for paints category')
            yield scrapy.Request(url, callback=self.parse_page_url, meta={'url_l3': str(url), 'url_l1': str(url_l1)}, )

        for href in response.xpath(self.getAllWoodsubcatsXpath):
            url = response.urljoin(href.extract())
            url_l1 = response.meta.get('url_l1')
            logging.info(f'url_l1 is {url_l1} for wood category')
            yield scrapy.Request(url, callback=self.parse_page_url, meta={'url_l3': str(url), 'url_l1': str(url_l1)}, )

        for href in response.xpath(self.getAllAccessoriesXpath):
            url = response.urljoin(href.extract())
            url_l1 = response.meta.get('url_l1')
            logging.info(f'url_l1 is {url_l1} for accessories category')
            yield scrapy.Request(url, callback=self.parse_page_url, meta={'url_l3': str(url), 'url_l1': str(url_l1)}, )

        for href in response.xpath(self.getAllWallpapersXpath):
            url = response.urljoin(href.extract())
            url_l1 = response.meta.get('url_l1')
            logging.info(f'url_l1 is {url_l1} for wallpapers category')
            yield scrapy.Request(url, callback=self.parse_page_url, meta={'url_l3': str(url), 'url_l1': str(url_l1)}, )

    def parse_page_url(self, response):
        for count in response.xpath(self.GetProductCountXpath):
            count_url = count.extract()
            url_l3 = response.meta.get('url_l3')
            url_l1 = response.meta.get('url_l1')
            paginated_url = url_l3 + "?count=" + str(count_url)
            logging.info(f'full pathway: {url_l1} > {url_l3} > {paginated_url}')

            yield scrapy.Request(paginated_url, callback=self.parse_main_item, dont_filter=True,
                                 meta={'url_l1': str(url_l1), 'url_l3': str(url_l3), 'count_url': count_url}, )
            # yield scrapy.Request(url="https://www.duluxdecoratorcentre.co.uk/special-offers", callback=self.parse_main_item, dont_filter=True)
            # Need to also add a separate yield for the special offers page, which doesn't have sub category links and so doesn't get passed to main parse

    def parse_main_item(self, response):
        # host = DdcMonitorSpider.start_urls

        # NOTE(yuri): there are multiple products per page, so we should generate a list of products right?
        # I create a dictionary of items by their product ID. I do this because when I fetch the price information
        # later, I will need to match up the price with the proper product ID.
        items_by_id = {}
        count_url = response.meta['count_url']
        url_l3 = response.meta['url_l3']
        url_l2_reg = re.compile(r'\bper.*\b')
        url_l2 = url_l2_reg.findall(url_l3)
        url_l1 = response.meta['url_l1']
        # url_l3 = re.sub("^.*\/([^\d]*)/.*$", "", url_l2).strip() - regex to get everything between the last and second to last /

        for product in zip(
                response.xpath(self.price_IDXpath).extract(),
                response.xpath(self.ProductNamesXpath).extract(),
                response.xpath(self.ProductLinksXpath).extract(),
                response.xpath(self.ProductImagesXpath).extract(),
                response.xpath(self.catlevel1Xpath).extract(),
                response.xpath(self.catlevel2Xpath).extract(),
                response.xpath(self.catlevel3Xpath).extract(),
        ):
            host = 'https://www.duluxdecoratorcentre.co.uk'
            item = PriceMonitorItem()
            item['product_id'] = product[0]
            item['product_name'] = product[1]
            item['product_url'] = host + product[2]
            item['product_image'] = product[3]
            item['retailer_site'] = host
            item['price_per_unit'] = None
            item['unit_measure'] = None
            item['number_of_units'] = None
            item['url_l3'] = url_l3
            item['url_l2'] = url_l2
            item['url_l1'] = url_l1
            item['cat_level3'] = product[6]
            item['cat_level2'] = product[5]
            item['cat_level1'] = product[4]
            item['was_price'] = None
            item['promo_description'] = None

            # set item into our dictionary by id
            items_by_id[product[0]] = item

            if item['product_name'] is None:
                logging.info(f'item returned no info: {response.url}')

        # this function is called after the price information has been fetched
        def price_form_callback(response):
            # populate the price information of each item and then return our items
            for price_info in json.loads(response.text):
                product_id = price_info['Id']
                price = price_info['PriceExclVat']
                price_formatted = re.sub("[^\d\.]", "", price)

                # lookup the product by id and update it's price field
                if product_id in items_by_id:
                    items_by_id[product_id]['price_excl'] = float(price_formatted)

            # return all the items found
            if len(items_by_id) != int(count_url):
                logging.info(f'found {len(items_by_id)} prices but page contained {count_url} items')


            #yield all of the items from the main parse function
            for items in items_by_id.values():
                yield items

        self.total_items = 0
        self.total_items += len(items_by_id)

        # use FormRequest to do a proper form post (source: https://docs.scrapy.org/en/latest/topics/request-response.html#using-formrequest-to-send-data-via-http-post)
        post_url = "https://www.duluxdecoratorcentre.co.uk/productlist/postloadproductgroups"
        yield FormRequest(post_url,
                          formdata=dict(ids=list(items_by_id.keys())),
                          callback=price_form_callback
                          )

        total_entries = self.crawler.stats.set_value("Total items scraped", self.total_items, spider=DdcMonitorSpider)
        yield total_entries


# class ExtensionThatAccessStats(object):
#     def __init__(self, stats):
#         self.stats = stats
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         key_stats = StatsCollector.get_stats(spider=DdcMonitorSpider)
#         total_items = StatsCollector.set_value("Total items scraped", self.total_items, spider=DdcMonitorSpider)
#
#         return key_stats





