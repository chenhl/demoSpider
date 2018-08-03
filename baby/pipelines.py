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
import hashlib
from urllib.parse import quote

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
'''
此示例演示如何从方法返回Deferredprocess_item()。
它使用Splash来呈现项目网址的屏幕截图。
Pipeline请求本地运行的Splash实例。
在请求被下载并且Deferred回调触发后，它将项目保存到一个文件并将文件名添加到项目。
'''
class ScreenshotPipeline(object):
    """Pipeline that uses Splash to render screenshot of
    every Scrapy item."""

    SPLASH_URL = "http://localhost:8050/render.png?url={}"

    def process_item(self, item, spider):
        encoded_item_url = quote(item["url"])
        screenshot_url = self.SPLASH_URL.format(encoded_item_url)
        request = scrapy.Request(screenshot_url)
        dfd = spider.crawler.engine.download(request, spider)
        dfd.addBoth(self.return_item, item)
        return dfd

    def return_item(self, response, item):
        if response.status != 200:
            # Error happened, return item.
            return item

        # Save screenshot to file, filename will be hash of url.
        url = item["url"]
        url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
        filename = "{}.png".format(url_hash)
        with open(filename, "wb") as f:
            f.write(response.body)

        # Store filename in item.
        item["screenshot_filename"] = filename
        return item
