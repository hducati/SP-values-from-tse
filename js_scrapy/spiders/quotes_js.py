# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver


class QuotesJsSpider(scrapy.Spider):
    name = 'quotes_js'
    start_urls = ['https://quotes.toscrape.com/js/']

    def __init__(self, *args, **kwargs):
        self.driver = webdriver.PhantomJS()
        super(QuotesJsSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        self.driver.get(response.url)
        sel = scrapy.Selector(text=self.driver.page_source)

        for quote in sel.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.text::text').extract_first(),
                'tags': quote.css('a.tag::text').extract(),
            }

        next_page_url = response.css('li.next a::attr(href)').extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
