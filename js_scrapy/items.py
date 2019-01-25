# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class JsScrapyItem(scrapy.Item):

    frame = Field()
    abrangencia = Field()
    quantidade = Field()
    porcentagem  =Field()
