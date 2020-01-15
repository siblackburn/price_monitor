# import scrapy
# from scrapy.http import FormRequest
# from scrapy import Request
# from scrapy.http import response
# from scrapy.shell import inspect_response
# from price_monitor.items import PriceMonitorItem
#
# class TestSpider(scrapy.Spider):
#     name = 'test_spider'
#     allowed_domains = ['duluxdecoratorcentre.co.uk']
#     start_urls = ['https://www.duluxdecoratorcentre.co.uk/product/wallpaper/cream-wallpaper']
#
#     def parse_prices(self, response):
#
#         # self.price_IDXpath = '//*[@id="list-of-products"]/li/@data-id'
#         # product_id_list = []
#         # for ids in response.xpath(self.price_IDXpath).extract():
#         #     product_id = "ids%5B%5D=" + ids + "&"
#         #     product_id_list.append(product_id)
#
#
#         # frmdata = product_id_list
#         post_url = "https://www.duluxdecoratorcentre.co.uk/productlist/postloadproductgroups"
#         # yield FormRequest(post_url,
#         #                 headers={
#         #                     'Content-Type': "application/x-www-form-urlencoded"
#         #                 },
#         #                 callback=self.parse,
#         #                 formdata=frmdata,
#         #                 method="POST")
#
#         request = scrapy.http.Request(url=post_url, method='POST',
#                                  headers={'Content-Type': 'application/x-www-form-urlencoded'},
#                                  body='ids%5B%5D=01aa622c-6760-4f04-a2ba-ca236b24841f&ids%5B%5D=f9a6f043-146e-4e3e-acce-8d814545b78a&ids%5B%5D=cc74018d-8fe0-4b8a-be70-51d2da64f2c6&ids%5B%5D=ac205d34-512c-4cec-8b5f-c98e7b2af8f1&ids%5B%5D=2d53301a-a4f5-46e4-978f-c5a155bb12af&ids%5B%5D=9d70289a-d184-4773-bc1a-ecdab2fa8675&ids%5B%5D=cafd21b1-305e-4d9a-8ba7-107825a425cc&ids%5B%5D=bc6e4b40-b4cc-48b2-a366-aa6300a6fe55&ids%5B%5D=877e9f0f-f23e-49ee-b0a0-a96100f9c07d'
#                                   , callback=self.parse)
#         request.meta['data'] = 'item'
#         yield request
#
#
#
#
#
#
#
#         # print("product id list", product_id_list)
#         # print(response.xpath(self.price_IDXpath).extract())
