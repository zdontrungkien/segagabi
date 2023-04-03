import scrapy
import requests

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.css("div.quote"):
            data = {
                "name": quote.css("small.author::text").extract_first(),
                "desc": quote.css("span.text::text").extract_first()
            }

            rsp = requests.post("http://web:8989/api/v1/seg",json=data)
            return rsp.json()
