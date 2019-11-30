import unittest
from price_monitor.spiders import DdcMonitorSpider
import price_monitor.items
from price_monitor import PriceMonitorItem, PriceMonitorCategories, PriceMonitorPipeline
from price_monitor import Listings
import scrapy

class testDdcSpider(unittest.TestCase):
    def setUp(self):
        self.spider = DdcMonitorSpider.DirectorySpider()

    def test_parsemain(self):
        ddc_spider = DdcMonitorSpider()
        test_parse = ddc_spider.parse('www.duluxdecoratorcentre.co.uk')

        self.assertIsNotNone(test_parse.response, msg="Response returned nothing")




