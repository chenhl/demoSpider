# -*- coding: utf-8 -*-
import scrapy
from baby.items import myBaseItem, newsSohuItem

from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit, urlparse, urljoin
import time
import datetime
import json
import pymysql
from scrapy.exceptions import DropItem

# item loader
class DefaultItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    pass


class newsSohuSpider(CrawlSpider):
    # https://news.artron.net//morenews/list732/
    # http: // comment.artron.net / column
    # 艺术家（认证过的）修改自己的简介，可排名提前
    name = 'news.sohu'
    catid = 6
    typeid = 0
    sysadd = 1
    status = 99

    # allowed_domains = ['artist.meishujia.cn']
    start_urls = [
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=10&size=20",
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=9&size=20",
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=8&size=20",
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=7&size=20",
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=6&size=20",
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=5&size=20",
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=4&size=20",
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=3&size=20",
                  "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=2&size=20",
                  "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=1&size=20",
                  ]
    # 设置下载延时
    download_delay = 10
    custom_settings = {
        'ITEM_PIPELINES': {
            'baby.pipelines.baseItemPipeline': 200,
            'baby.pipelines.itemExistsPipeline': 260,
            'baby.pipelines.newsSohuPipeline': 300,
            'baby.pipelines.MyImagesPipeline': 400,
            'baby.pipelines.MysqlWriterPipeline': 500,
        },
        'COOKIES_ENABLED': False,
        # 'REFERER_ENABLED': True, #默认为True
    }

    def parse(self, response):
        base_url = "http://www.sohu.com/a/"
        js = json.loads(response.body_as_unicode())
        for item in js:
            id = item["id"]
            aid = item["authorId"]
            url = base_url + str(id) + "_" + str(aid)
            yield scrapy.Request(url, callback=self.parse_item, meta=item, dont_filter=False) # dont_filter 默认就是False去重，scrapy crawl news.sohu -s JOBDIR=crawls/news_sohu 启用持久化spider,jobdir保存了爬取过的url的hash
            # else:
            #     raise DropItem("Duplicate item found: %s" % item)
        # pass

    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=newsSohuItem(), selector=response)
        l.add_value('spider_link', get_base_url(response))
        l.add_xpath('title', 'normalize-space(//div[re:test(@class,"text-title")]//h1)')
        l.add_xpath('content', '//article/node()')
        # l.add_value('content', 'abc')
        # // *[ @ id = "mp-editor"]
        l.add_value('keywords', '')
        l.add_value('description', '')
        # imgs = json.dump(response.meta['images'])authorName authorPic
        l.add_value('spider_name', self.name)
        l.add_value('spider_imgs', response.meta['images'])
        l.add_value('spider_userpic', response.meta['authorPic'])
        l.add_value('spider_img', response.meta['picUrl'])
        l.add_value('spider_tags', response.meta['tags'])

        l.add_value('uid', response.meta['authorId'])
        l.add_value('uname', response.meta['authorName'])
        l.add_value('aid', response.meta['id'])


        l.add_value('catid', self.catid)
        l.add_value('status', self.status)
        l.add_value('sysadd', self.sysadd)
        l.add_value('typeid', self.typeid)
        l.add_value('inputtime', int(time.time()))
        l.add_value('updatetime', int(time.time()))
        l.add_value('create_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        l.add_value('update_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td')
        # l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//text()')

        d = l.load_item()
        yield d

    def parse_content_item(self, selector):
        pass
