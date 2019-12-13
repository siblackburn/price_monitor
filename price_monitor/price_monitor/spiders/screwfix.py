# # -*- coding: utf-8 -*-
# import scrapy
# import logging
# from urllib.parse import urlparse
# import urllib.parse
# from scrapy.exporters import CsvItemExporter
# import urljoin
# from scrapy import Request
# from scrapy.spiders import CrawlSpider, Rule
# from price_monitor.items import PriceMonitorItem
# from scrapy.linkextractors import LinkExtractor
# import re
#
# class ScrewfixSpider(CrawlSpider):
#     name = 'sf_monitor'
#     allowed_domains = ['screwfix.com']
#     start_urls = ['https://www.screwfix.com/c/decorating/cat850130']
#
#     rules = Rule(LinkExtractor(allow='(/c/decorating)'), callback='parse_main_item', follow=True),
#
#     def parse_main_item(self, response):
#         host = 'https://www.screwfix.com'
#         url_l3 = str(response.url)
#         logging.info(f'{host} is type {type(host)} ')
#         logging.info(f'attempting to scrape {url_l3}')
#
#         ProductBoxXpath = '//*[contains(@id, "product_box")]'
#         # response_box = response.xpath(productBoxXpath).extract()
#
#         for product in response.xpath(ProductBoxXpath):
#             url_l1 = response.xpath('string(//*[@id="breadcrumb_item_search_result_2_top"]/@href)').extract()
#             cat_level1 = response.xpath('//*[@id="breadcrumb_item_search_result_2_top"]/span/text()').extract()
#             cat_level2 = response.xpath('//*[@id="breadcrumb_item_search_result_3_top"]/span/text()').extract()
#             cat_level3 = response.xpath('//*[@id="breadcrumb_item_search_result_4_top"]/span/text()').extract()
#             prod_id = product.xpath('//*[contains(@id, "product_quote")]/@quotenumberproductid').extract()
#             prod_name = product.xpath('//*[contains(@id, "product_description")]/@title').extract()
#             logging.info(f'prod name is {prod_name}')
#             prod_link = product.xpath('//*[contains(@id, "product_description")]/@href').extract()
#             prod_image = product.xpath('//*[contains(@id, "product_image")]/@src').extract()
#             price_inc = product.xpath('//*[contains(@id, "product_list_price")]/text()').extract()
#             promo_offer = product.xpath('//*[contains(@id, "productID")]/div[3]/div/div/div/span/text()').extract()
#             was_price = product.xpath('//*[contains(@id, "addToTrolleyForm")]/div/div[1]/div[2]/span[1]/text()').extract()
#             logging.info(f'was price is {was_price} for {prod_name}')
#             price_formatted = re.sub("[^\d\.]", "", price_inc)
#             price_excl = round(float(price_formatted) / 1.2, 2)
#             was_price_formatting = re.sub("[^\d\.]", "", was_price)
#             was_price_excl = round(float(was_price_formatting)/1.2, 2)
#
#
#             item = PriceMonitorItem()
#             item['product_id'] = prod_id
#             item['product_name'] = prod_name
#             item['product_url'] = prod_link
#             item['product_image'] = prod_image
#             item['price_excl'] = price_excl
#             item['retailer_site'] = host
#             item['price_per_unit'] = None
#             item['unit_measure'] = None
#             item['number_of_units'] = None
#             item['url_l3'] = url_l3
#             item['url_l2'] = None
#             item['url_l1'] = url_l1
#             item['cat_level3'] = cat_level3
#             item['cat_level2'] = cat_level2
#             item['cat_level1'] = cat_level1
#             item['was_price'] = was_price_excl
#             item['promo_description'] = promo_offer
#
#             if (item['product_name'] or item['price_excl'] or item['retailer'] or item['product_url']) is None:
#                 logging.WARNING(f'item returned no info: {response.url}')
#
#             yield item
#
