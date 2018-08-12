# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst

class BabyDetailItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    cur_link = scrapy.Field()
    pass

class BabyItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(
        output_processor=TakeFirst()
    )
    image_paths = scrapy.Field()
    image_urls = scrapy.Field(
        output_processor=TakeFirst()
    )
    cur_link = scrapy.Field()
    image_urls = scrapy.Field(
        output_processor=TakeFirst()
    )
    shop_price = scrapy.Field(
        output_processor=TakeFirst()
    )
    market_price = scrapy.Field(
        output_processor=TakeFirst()
    )
    pass

class artistMeishujiaItem(scrapy.Item):
    name = scrapy.Field(
        output_processor=TakeFirst()
    )
    image_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    spider_link = scrapy.Field(
        output_processor=TakeFirst()
    )
    content = scrapy.Field(
        # output_processor=TakeFirst()
    )
