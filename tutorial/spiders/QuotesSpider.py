import scrapy
from bs4 import BeautifulSoup

from tutorial.items import TutorialItem


class QuotesspiderSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        bs_obj = BeautifulSoup(response.text)
        items = bs_obj.find_all('div', {'class': 'quote'})  # 获取列表
        for item in items:
            item_field = TutorialItem()  # 每一个item信息存储到item_field里
            text = item.find('span', {'itemprop': 'text', 'class': 'text'}).text
            author = item.find('small', {'class': 'author'}).text
            tags = item.find_all('a', {'class': 'tag'})
            tags = [tag.text for tag in tags]  # 获取tags列表里的每一个tag的文本
            item_field['text'] = text  # 存储数据到item_field
            item_field['author'] = author
            item_field['tags'] = tags
            self.logger.info(item_field['text'])
            yield item_field  # 使用生成器，每次调用都会从结束处开始，会生成新的item_field，爬取和计算后会返回数据

        # 获取下一页，由于使用BeautifulSoup比较麻烦，而且错误处理比较不方便，所以使用css选择器
        next_page = response.css('.pager .next a::attr(href)').extract_first()
        # 如果next_page存在
        if next_page:
            # 使用urljoin获取绝对地址
            next_url = response.urljoin(next_page)
            # 回调函数，继续调用该parse函数，传入next_url进行请求
            yield scrapy.Request(url=next_url, callback=self.parse)
