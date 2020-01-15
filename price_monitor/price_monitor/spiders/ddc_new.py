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
import json
from scrapy.http import FormRequest

class DDCSpider(CrawlSpider):
    name = 'ddc_monitor'
    allowed_domains = ['duluxdecoratorcentre.co.uk']
    start_urls = ['https://www.duluxdecoratorcentre.co.uk/products/paint', 'https://www.duluxdecoratorcentre.co.uk/woodcare']

    rules = Rule(LinkExtractor(
        allow=['/'],
        deny=['returnurl', 'returnUrl']), callback='parse_main_item', follow=True),

    def parse_main_item(self, response):
        host = 'https://www.duluxdecoratorcentre.co.uk'
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
        self.PageNotFoundXpath = 'normalize-space(//*[@id="productListPage"]/div/text())'  # not currently used. This returns the text "PageNotFound" if the page isn't found
        self.price_IDXpath = '//*[@id="list-of-products"]/li/@data-id'
        self.catlevel3Xpath = '/html/body/div[1]/div[3]/div/div[1]/div/ul/li[4]/a/text()'  # once on a page with products
        self.catlevel2Xpath = '/html/body/div[1]/div[3]/div/div[1]/div/ul/li[3]/a/text()'
        self.catlevel1Xpath = '/html/body/div[1]/div[3]/div/div[1]/div/ul/li[2]/a/text()'

        items_by_id = {}
        for product in zip(
            response.xpath(self.price_IDXpath).extract(),
            response.xpath(self.ProductNamesXpath).extract(),
            response.xpath(self.ProductLinksXpath).extract(),
            response.xpath(self.ProductImagesXpath).extract(),
            response.xpath(self.catlevel1Xpath).extract(),
            response.xpath(self.catlevel2Xpath).extract(),
            response.xpath(self.catlevel3Xpath).extract()
        ):
            logging.info(f'product being zipped is {product[1]}')
            item = PriceMonitorItem()
            item['product_id'] = product[0]
            item['product_name'] = product[1]
            item['product_url'] = str('https://www.duluxdecoratorcentre.co.uk' + product[2])
            item['product_image'] = product[3]
            item['retailer_site'] = 'https://www.duluxdecoratorcentre.co.uk'
            item['price_per_unit'] = None
            item['unit_measure'] = None
            item['number_of_units'] = None
            item['url_l3'] = None
            item['url_l2'] = None
            item['url_l1'] = None
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
            logging.info(f'before form callback, items by id length is {len(items_by_id)}')
            logging.info(f'items by id before price form are {items_by_id}')
            # populate the price information of each item and then return our items
            for price_info in json.loads(response.text):
                logging.info(f'price info is {price_info}')
                product_id = price_info['Id']
                price = price_info['PriceExclVat']
                price_formatted = re.sub("[^\d\.]", "", price)

                # lookup the product by id and update it's price field
                if product_id in items_by_id:
                    items_by_id[product_id]['price_excl'] = float(price_formatted)

            #yield all of the items from the main parse function
            for items in items_by_id.values():
                yield items

        # use FormRequest to do a proper form post (source: https://docs.scrapy.org/en/latest/topics/request-response.html#using-formrequest-to-send-data-via-http-post)
        post_url = "https://www.duluxdecoratorcentre.co.uk/productlist/postloadproductgroups"
        yield FormRequest(post_url,
                          formdata=dict(ids=list(items_by_id.keys())),
                          callback=price_form_callback
                          )
        logging.info(f'items by id are {items_by_id.keys()}')