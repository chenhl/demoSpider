# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import logging
from scrapy.exceptions import DropItem
class BabyPipeline(object):
    def process_item(self, item, spider):
        # pass
        if float(item['shop_price']) > 10.0:
            return item
        else:
            raise DropItem("Missing price in %s" % item)

class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item