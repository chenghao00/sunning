# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SunningItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    parent_type = scrapy.Field()
    m_cate = scrapy.Field()
    s_cate = scrapy.Field()
    s_href = scrapy.Field()
    book_name = scrapy.Field()
    book_href = scrapy.Field()
    book_price = scrapy.Field()
