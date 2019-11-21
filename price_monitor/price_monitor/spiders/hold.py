# Attempt 1
#
# links = response.xpath('//div/a/@href').extract()
#         for link in links:
#
#             scheme = urlparse(link).scheme
#             homepage = urlparse(link).netloc
#             complete_url = urllib.parse.urljoin(response.url, link.strip())
#             print(complete_url)

            # with open("ddc_test.csv", "w") as initial_file:
            #     exporter = CsvItemExporter(initial_file)
            #     exporter.fields_to_export = complete_url
            #     exporter.start_exporting()
            #
            # yield complete_url

            # url = link.get()
            # if link not in test_list:
            #     test_list.append(complete_url)



            # print("my list", test_list)



#Attempt 2. Pricemonitoritem object not being retrieved from the project structure. Unsure why
# class DdcMonitorSpider(scrapy.Spider):
#     name = 'ddc_monitor'
#     allowed_domains = ['www.duluxdecoratorcentre.co.uk']
#     start_urls = ['https://www.duluxdecoratorcentre.co.uk/products/paint',
#                   'https://www.duluxdecoratorcentre.co.uk/woodcare',
#                   'https://www.duluxdecoratorcentre.co.uk/products/accessories',
#                   'https://www.duluxdecoratorcentre.co.uk/special-offers'
#                   ]
#
#     custom_settings = {
#         'DEPTH_LIMIT': 10
#     }
#
#     def parse(self, response):
#         self.item = PriceMonitorItem()
#         self.item['url'] = response.url
#         self.item['next_url'] = response.xpath('//div/a/@href').extract()
#
#         yield self.item

#Attempt 4: initial parse of product links seems to be working
# def parse(self, response):
#     items = PriceMonitorItem()
#     test_list = []
#     products = response.xpath('//body//div[@class="product-container"]')
#     for product in products:
#         # image = product.xpath('div[@class="product-img"]/a/img/@src').extract_first()
#         link = product.xpath('div[@class="product-title"]/a/@href').extract()
#         # name = product.xpath('div[@class="product-description"]/p/a/text()').extract_first()
#         # price = product.xpath(
#         #     'div[@class="price-excl-wrapper highlight"]/span[@class="lbl-excl-vat-price"]/text()').extract_first()
#         if link not in test_list:
#             test_list.append(link)
#     yield test_list
#     print("Scraped", test_list)

