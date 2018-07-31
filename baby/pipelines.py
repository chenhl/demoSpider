# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import logging
from scrapy.exceptions import DropItem
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class BabyPipeline(object):
    def process_item(self, item, spider):
        # pass
        if float(item['shop_price']) > 10.0:
            return item
        else:
            raise DropItem("Missing price in %s" % item)

class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('data/items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        # for image_url in item['image_urls']:
        yield scrapy.Request(item['image_urls'])

    def item_completed(self, results, item, info):
        # for ok, x in results:
        #     if ok:
        #         print(x['path'])
        # result是一个包含tuple的容器
        # 容器中每个元素包含两个值，第一个代表状态True / False，第二个值是一个dict
        # 如果元素中状态为True则取dict中的path值
        # PEP0202列表递推式 https://www.python.org/dev/peps/pep-0202/


        # image_paths = [x['path'] for ok, x in results if ok]
        # if not image_paths:
        #     raise DropItem("Item contains no images")
        # item['image_paths'] = image_paths
        return item