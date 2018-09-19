# -*- coding: utf-8 -*-
import scrapy
from baby.items import artistMeishujiaItem

from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit,urlparse,urljoin
import time
import datetime
import json

#item loader
class DefaultItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    pass
class newsSohuSpider(CrawlSpider):
    #https://news.artron.net//morenews/list732/
    # http: // comment.artron.net / column
    #艺术家（认证过的）修改自己的简介，可排名提前
    name = 'news.sohu'
    catid=6
    typeid=0
    sysadd=1
    status=99

    # allowed_domains = ['artist.meishujia.cn']
    start_urls = ["http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=1&size=3",
                  # "http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=57132&page=2&size=20",
                  ]
    # 设置下载延时
    download_delay = 10
    custom_settings = {
        'ITEM_PIPELINES': {
                    'baby.pipelines.artPipeline': 300,
                    'baby.pipelines.MyImagesPipeline': 400,
                    'baby.pipelines.MysqlWriterPipeline': 500,
        },
        'COOKIES_ENABLED':False,
    }

    def parse(self, response):
        base_url = "http://www.sohu.com/a/"
        # print(base_url)
        # print("#############")
        js = json.loads(response.body_as_unicode())
        # print(js)
        for item in js:
            id=item["id"]
            print(id)
            aid=item["authorId"]
            print(aid)
            url=base_url+str(id)+"_"+str(aid)
            print(url)
            yield scrapy.Request(url,callback=self.parse_item,meta=item)
        # pass

    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=artistMeishujiaItem(),selector=response)
        l.add_value('spider_link', get_base_url(response))
        l.add_xpath('title', 'normalize-space(//div[re:test(@class,"text-title")]//h1)')
        l.add_xpath('content', '//article/node()')
        # l.add_value('content', 'abc')
        # // *[ @ id = "mp-editor"]
        l.add_value('keywords', '')
        l.add_value('description', '')

        # imgs = json.dump(response.meta['images'])
        if not response.meta['images']:
            l.add_value('spider_imgs', [])
        else:
            l.add_value('spider_imgs', response.meta['images'])
        if not response.meta['picUrl']:
            l.add_value('spider_img','')
        else:
            l.add_value('spider_img', response.meta['picUrl'])

        l.add_value('catid', self.catid)
        l.add_value('status', self.status)
        l.add_value('sysadd', self.sysadd)
        l.add_value('typeid', self.typeid)
        l.add_value('inputtime',int(time.time()))
        l.add_value('updatetime', int(time.time()))
        l.add_value('create_time',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        l.add_value('update_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td')

        # l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//text()')

        d = l.load_item()
        yield d

    def parse_content_item(self, selector):
        pass