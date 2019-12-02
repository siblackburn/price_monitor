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
import re


class TradePointSpider(scrapy.Spider):
    name = 'tp_monitor'
    allowed_domains = ['trade-point.co.uk']
    start_urls = ['https://www.trade-point.co.uk/']

    def __init__(self):
        self.declare_xpath()

    def declare_xpath(self):
        self.getAllCategoriesXpath = '//*[@id="site-nav"]/div/ul/li[6]/div/div/div/div/a/@href'  # TP categry links > yo return painting and decorating href. e.g. paint
        self.getAllSubCategoriesXpath = '//*[@id="content"]/div/div/div[2]/div[1]/div/section[1]/div/ul/li/div/article/div/div/h3/a/@href'  # TP all sub categories, e.g.interior emulsion
        self.getAllMicroCategoriesXpath = '//*[@id="content"]/div/div/div[2]/div[1]/div/section[1]/div/ul/li/div/article/div/div/h3/a/@href' #each TP micro cat - e.g. bathroom paint
        self.getALLPagesXpath = '//*[@id="ui-jump-hook"]/ul/li[last()-1]/a/@href' #return all paginated pages (e.g. page=4)

        self.ProductLinksXpath = '//*[@id]/div/div/h3/a/@href' # all product links: TP
        self.ProductNamesXpath = '//*[@id]/div/div/h3/a/text()'  # product names in text: TP
        self.ProductImagesXpath = '//*[@id]/a/img/@src'  #link to TP images
        self.PricePoundsXpath = '//*[@id]/div[1]/div[2]/div/p[2]/strong/span/span[2]/text()'
        self.PricePenceXpath = '//*[@id]/div[1]/div[2]/div/p[2]/strong/span/span[4]/text()'

        self.PricePerUnitPoundsXpath = '//*[@id]/div[1]/div[1]/p/span/span[2]/text()'
        self.PricePerUnitPenceXpath = '//*[@id]/div[1]/div[1]/p/span/span[4]/text()'
        self.UnitofMeasureXpath = 'normalize-space(//*[@id]/div/div[1]/p/text())'

    def parse(self, response):
        for href in response.xpath(self.getAllCategoriesXpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url=url, callback=self.parse_category, dont_filter=True, meta={'url_l4' : url})

    def parse_category(self, response):   #gets passed a category (e.g. paint)
        for href in response.xpath(self.getAllSubCategoriesXpath):
            url = response.urljoin(href.extract())
            url_l4 = response.meta.get('url_l4')
            yield scrapy.Request(url, callback=self.parse_subcategory, dont_filter=True, meta={'url_l4':str(url_l4), 'url_l3':str(url)} )

    def parse_subcategory(self, response): #gets passed a sub category (e.g. interior emulsion) and then passed on a micro cat (e.g. wall and ceiling paint)
        for href in response.xpath(self.getAllMicroCategoriesXpath):
            url = response.urljoin(href.extract())
            url_l4 = response.meta.get('url_l4')
            url_l3 = response.meta.get('url_l3')
            logging.info(f'extracted micro category URL: {url}')
            yield scrapy.Request(url, callback=self.parse_main_item, dont_filter=True, meta={'url_l4':str(url_l4), 'url_l3':str(url_l3)} )

    # def parse_next_page(self, response):
    #     next_page_button = response.xpath(self.getALLPagesXpath).extract()
    #     url_l4 = response.meta.get('url_l4')
    #     while next_page_button:
    #         yield scrapy.Request(next_page_button, callback=self.parse_main_item, dont_filter=True, meta={'url_l4':str(url_l4), 'url_l3':str(next_page_button)} )

    def parse_main_item(self, response):
        host = TradePointSpider.start_urls
        url_l2 = str(response.url)
        url_l3 = response.meta.get('url_l3')
        url_l4 = response.meta.get('url_l4')

        logging.info(f'attempting to scrape {url_l2} coming from {url_l3} > {url_l4}')

        for product in zip(
            response.xpath(self.ProductNamesXpath).extract(),
            response.xpath(self.ProductLinksXpath).extract(),
            response.xpath(self.ProductImagesXpath).extract(),
            response.xpath(self.PricePoundsXpath).extract(),
            response.xpath(self.PricePenceXpath).extract(),
            response.xpath(self.PricePerUnitPoundsXpath).extract(),
            response.xpath(self.PricePerUnitPenceXpath).extract(),
            response.xpath(self.UnitofMeasureXpath).extract(),
        ):

            logging.info(f'There are {len(product)} products found')

            item = PriceMonitorItem()
            item['product_id'] = None
            item['product_name'] = product[0]
            item['product_url'] = product[1]
            item['product_image'] = product[2]
            item['price_excl'] = float(product[3] + "." + product[4])
            item['retailer_site'] = host
            item['price_per_unit'] = float(product[5] + "." + product[6])
            item['unit_measure'] = product[7]
            item['number_of_units'] = (item['price_excl'] / item['price_per_unit'])
            item['url_l4'] = url_l4
            item['url_l3'] = url_l3
            item['url_l2'] = url_l2

            if (item['product_name'] or item['price_excl'] or item['retailer'] or item['product_url']) is None:
                logging.info(f'item returned no info: {response.url}')

            yield item






    # def parse_page_url(self, response):
    #     for count in response.xpath(self.getALLPagesXpath):
    #         next_page = response.urljoin(count.extract())
    #         url_l4 = response.meta.get('url_l4')
    #         url_l3 = response.meta.get('url_l3')
    #         logging.warning(f'full pathway: {url_l4} > {url_l3} > {next_page}')
    #         yield scrapy.Request(url=next_page, callback=self.parse_main_item, dont_filter=True, meta={'url_l4':str(url_l4), 'url_l3':str(url_l3)} )


