import scrapy
from scrapy.selector import Selector
import requests
from bs4 import BeautifulSoup

class PeerSpider(scrapy.Spider):
    name = 'peer'
    allowed_domains = ['peerspot.com']
    start_urls = ['https://www.peerspot.com/products/snowflake-reviews/page-3']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }

    def parse(self, response):
        resp = requests.get(url=self.start_urls[0],headers=self.headers, verify=False)
        soup = BeautifulSoup(resp.text, 'lxml')
        data = soup.find_all('div',{'class': 'embedded-product-review1 embedded-review regular'})
        for item in data:
            review = item.find('div', {'class': 'review-content'})
            contents = review.findAll('div', {'class': 'gitb-section-content'})
            i = 0
            for content in contents:
                contents[i] = content.text.strip()
                i += 1
            payload = {
                'user': item.find('span',{'class': 'username'}).text.strip(),
                'date': item.find('div',{'class': 'review-date pull-flex-right'}).text,
                'title': review.find('div', {'class': 'review-title'}).text,
                'content': '. '.join(contents)
            }
            rsp = requests.post("http://web:8989/api/v1/seg",json=payload)
            print('--------rsp--------', rsp.json().get('id'))