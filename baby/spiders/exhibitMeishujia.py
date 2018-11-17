# -*- coding: utf-8 -*-
import scrapy
from baby.items import myBaseItem,exhibitMeishujiaItem

from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit,urlparse,urljoin
import time
import datetime
#item loader
class DefaultItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    pass
class exhibitMeishujiaSpider(CrawlSpider):
    name = 'exhibit.meishujia'
    catid=6
    typeid=0
    sysadd=1
    status=99

    # allowed_domains = ['artist.meishujia.cn']
    start_urls = ["http://exhibit.meishujia.cn/index.php?page=1&act=app&appid=4099"]
    # 设置下载延时
    download_delay = 1
    custom_settings = {
        'ITEM_PIPELINES': {
                    'baby.pipelines.exhibitPipeline': 300,
                    # 'baby.pipelines.JsonWriterPipeline': 350,
                    # 'baby.pipelines.MultiImagesPipeline': 400,
                    # 'baby.pipelines.MysqlWriterPipeline': 500,
        },
    }
    rules = (
        # 地址分页
        # Rule(LinkExtractor(allow=('/index.php?page=1&act=pps&smid=2'), allow_domains=('meishujia.cn'),restrict_xpaths=('//ul[@class="sert"]'))),
        # 详情页1
        # Rule(LinkExtractor(restrict_xpaths=('//li[@class="i42c"]/div[@class="i42ck"]'))),
        # 详情页 2 /?act=usite&usid=[0-9]{1,10}&inview=[a-z-0-9-]+&said=528  /?act=usite&usid=8646&inview=appid-241-mid-619&said=528
        #只有一个规则的时候，后面的“,”要加上，不然报 TypeError: 'Rule' object is not iterable 错误
        Rule(LinkExtractor(restrict_xpaths=('//dd[re:test(@class,"theme_body_1609")]//ul[@class="srre"]//div[@class="srremap"]/a')),callback='parse_item'),
    )
    def detail_lik(self,links):
        yield links

    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=exhibitMeishujiaItem(),selector=response)
        l.add_value('spider_link', get_base_url(response))
        l.add_xpath('spider_img', '//dd[re:test(@class,"theme_body_1611")]//ul[re:test(@class,"zl_r_af")]//img[@src]')
        l.add_value('spider_imgs', '//*[@id="photos"]//div[@class="panel"]')
        l.add_xpath('title', 'normalize-space(//dd[re:test(@class,"theme_body_1611")]//h1)')

        l.add_xpath('attr', '//dd[re:test(@class,"theme_body_1611")]/ol//text()')
        l.add_value('attr_value',[])

        l.add_xpath('content', '//dd[re:test(@class,"theme_body_1611")]//ul[re:test(@class,"zl_r_b zl_r_bt")]/node()')
        l.add_value('keywords', '')
        l.add_value('description', '')
        l.add_value('thumbs', '')
        l.add_value('catid',self.catid)
        l.add_value('status', self.status)
        l.add_value('sysadd', self.sysadd)
        l.add_value('typeid', self.typeid)
        l.add_value('inputtime',int(time.time()))
        l.add_value('updatetime', int(time.time()))
        l.add_value('create_time',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        l.add_value('update_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


        # l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td')
        # l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//text()')
        # l.add_xpath('attr', '//dd[re:test(@class,"theme_body_1611")]/ol/span/text()')
        # l.add_xpath('attr_value', '//dd[re:test(@class,"theme_body_1611")]/ol/text()')

        d = l.load_item()
        # print(d)
        yield d

    def parse_content_item(self, selector):
        pass