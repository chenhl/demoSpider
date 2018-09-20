# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst,Identity,Join, MapCompose
from w3lib.html import remove_tags
def myTakeFirst(value):
    if value:
        for val in value:
            if val is not None and val != '':
                return val
    return value

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
    catid = scrapy.Field(
        output_processor=TakeFirst()
    )
    typeid = scrapy.Field(
        output_processor=TakeFirst()
    )
    spider_link = scrapy.Field(
        output_processor=TakeFirst()
    )
    spider_img = scrapy.Field(
        # output_processor=Identity()
        output_processor=TakeFirst()
    )
    spider_imgs = scrapy.Field(
        # output_processor=Identity()
    )
    status = scrapy.Field(
        output_processor=TakeFirst()
    )
    sysadd = scrapy.Field(
        output_processor=TakeFirst()
    )
    inputtime = scrapy.Field(
        output_processor=TakeFirst()
    )
    updatetime = scrapy.Field(
        output_processor=TakeFirst()
    )
    create_time = scrapy.Field(
        output_processor=TakeFirst()
    )
    update_time = scrapy.Field(
        output_processor=TakeFirst()
    )
    username = scrapy.Field(
        output_processor=TakeFirst()
    )

    thumb = scrapy.Field(
        output_processor=TakeFirst()
    )
    thumbs = scrapy.Field(
        # output_processor=Identity()
    )
    title = scrapy.Field(
        output_processor=TakeFirst()
    )
    keywords = scrapy.Field(
        output_processor=TakeFirst()
    )
    description =scrapy.Field(
        output_processor=TakeFirst()
    )
    content = scrapy.Field(
        # output_processor=TakeFirst()
    )

class newsSohuItem(artistMeishujiaItem):
    spider_img = scrapy.Field(
        output_processor=TakeFirst()
        # input_processor=Identity(),
        # output_processor=MapCompose(myTakeFirst),
    )
    spider_imgs = scrapy.Field(
        # input_processor=Identity()
        # output_processor=TakeFirst()
    )
class exhibitMeishujiaItem(artistMeishujiaItem):
    attr = scrapy.Field(
        # output_processor=TakeFirst()
    )
    attr_value = scrapy.Field(
        # output_processor=TakeFirst()
    )
    pass