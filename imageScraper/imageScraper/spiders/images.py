import scrapy


class ImagesSpider(scrapy.Spider):
    name = "images"
    allowed_domains = ["www.upc.edu"]
    start_urls = ["https://www.upc.edu"]

    def parse(self, response):
        pass
