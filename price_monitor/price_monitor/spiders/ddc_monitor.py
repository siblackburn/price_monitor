# -*- coding: utf-8 -*-
import scrapy


class DdcMonitorSpider(scrapy.Spider):
    name = 'ddc_monitor'
    allowed_domains = ['www.duluxdecoratorcentre.co.uk']
    start_urls = ['https://www.duluxdecoratorcentre.co.uk/products/paint',
                  'https://www.duluxdecoratorcentre.co.uk/woodcare',
                  'https://www.duluxdecoratorcentre.co.uk/products/accessories',
                  'https://www.duluxdecoratorcentre.co.uk/special-offers'
                  ]


    def parse(self, response):
        test_list = []
        links = response.xpath('//a/@href')
        for link in links:
            url = link.get()
            if url is not test_list:
                test_list.append(url)

        print(test_list)