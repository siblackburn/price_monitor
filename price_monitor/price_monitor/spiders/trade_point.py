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


class TradePointSpider(CrawlSpider):
    name = 'tp_monitor'
    allowed_domains = ['trade-point.co.uk']
    start_urls = ['https://www.trade-point.co.uk']

    rules = Rule(LinkExtractor(allow=['/departments/painting-decorating', '/new-tradepoint/departments/painting-decorating'] ), callback='parse_main_item', follow=True),

    # def parse_next_page(self, response):
    #     next_page_button = response.xpath(self.getALLPagesXpath).extract()
    #     url_l4 = response.meta.get('url_l4')
    #     while next_page_button:
    #         yield scrapy.Request(next_page_button, callback=self.parse_main_item, dont_filter=True, meta={'url_l4':str(url_l4), 'url_l3':str(next_page_button)} )

    def parse_main_item(self, response):
        host = 'https://www.trade-point.co.uk'
        url_l2 = str(response.url)
        url_l3 = response.xpath('normalize-space(/html/body/div[1]/div[1]/div/nav/ul/li[last()-1]/a/@href)').extract()
        # url_l4 = response.xpath('/html/body/div[1]/div[1]/div/nav/ul/li[last()-2]/a/@href').extract() #isn't working due to the 2nd to last item starting with a #, e.g.

        logging.info(f'attempting to scrape {url_l2} coming from {url_l3}')

        getALLPagesXpath = '//*[@id="ui-jump-hook"]/ul/li[last()-1]/a/@href'  # return all paginated pages (e.g. page=4)
        ProductLinksXpath = '//*[@id]/div/div/h3/a/@href'  # all product links: TP
        ProductNamesXpath = '//*[@id]/div/div/h3/a/text()'  # product names in text: TP
        ProductImagesXpath = '//*[@id]/a/img/@src'  # link to TP images
        PricePoundsXpath = '//*[@id]/div[1]/div[2]/div/p[2]/strong/span/span[2]/text()'
        PricePenceXpath = '//*[@id]/div[1]/div[2]/div/p[2]/strong/span/span[4]/text()'
        PricePerUnitPoundsXpath = '//*[@id]/div[1]/div[1]/p/span/span[2]/text()'
        PricePerUnitPenceXpath = '//*[@id]/div[1]/div[1]/p/span/span[4]/text()'
        UnitofMeasureXpath = 'normalize-space(//*[@id]/div/div[1]/p/text())'


        for product in zip(
            response.xpath(ProductNamesXpath).extract(),
            response.xpath(ProductLinksXpath).extract(),
            response.xpath(ProductImagesXpath).extract(),
            response.xpath(PricePoundsXpath).extract(),
            response.xpath(PricePenceXpath).extract(),
            response.xpath(PricePerUnitPoundsXpath).extract(),
            response.xpath(PricePerUnitPenceXpath).extract(),
            response.xpath(UnitofMeasureXpath).extract(),
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
            item['number_of_units'] = float(round((item['price_excl'] / item['price_per_unit']), 3))
            item['url_l4'] = None
            item['url_l3'] = url_l3
            item['url_l2'] = url_l2

            if (item['product_name'] or item['price_excl'] or item['retailer'] or item['product_url']) is None:
                logging.info(f'item returned no info: {response.url}')

            yield item

