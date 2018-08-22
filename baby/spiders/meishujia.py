# -*- coding: utf-8 -*-
import scrapy
from baby.items import artistMeishujiaItem

from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit,urlparse,urljoin
from datetime import time,datetime

#item loader
class DefaultItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    pass
class MeishujiaSpider(CrawlSpider):
    name = 'artist.meishujia'
    catid=6
    typeid=0
    sysadd=1

    # allowed_domains = ['artist.meishujia.cn']
    start_urls = ["http://artist.meishujia.cn/index.php?act=pps&smid=2"]
    # 设置下载延时
    download_delay = 1
    custom_settings = {
        'ITEM_PIPELINES': {
                    'baby.pipelines.artPipeline': 300,
                    'baby.pipelines.MysqlWriterPipeline': 500,
        },

    }
    rules = (
        # 地址分页
        # Rule(LinkExtractor(allow=('/index.php?page=1&act=pps&smid=2'), allow_domains=('meishujia.cn'),restrict_xpaths=('//ul[@class="sert"]'))),
        # 详情页1
        Rule(LinkExtractor(restrict_xpaths=('//li[@class="i42c"]/div[@class="i42ck"]'))),
        # 详情页 2 /?act=usite&usid=[0-9]{1,10}&inview=[a-z-0-9-]+&said=528  /?act=usite&usid=8646&inview=appid-241-mid-619&said=528
        Rule(LinkExtractor(restrict_css=('.theme_title_4647 a')),process_links=('detail_link'),
          callback='parse_item')
    )
    def detail_lik(self,links):
        yield links[0]

    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=artistMeishujiaItem(),selector=response)
        l.add_value('spider_link', get_base_url(response))
        l.add_css('thumb', '.theme_body_4656 table:nth-child(2) tr:nth-child(1) td:nth-child(1) img::attr(src)')
        l.add_xpath('title', 'normalize-space(//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[2]/td)')
        # normalize-space 去除 html \r\n\t
        # re 正则表达式，class只要包含theme_body_4656
        # l.add_xpath('content', 'normalize-space(//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td)')
        # content=""for selector in sel.xpath('//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//p'): content=content+ selector.xpath("/text()").extract()

        # for sele in response.xpath('//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//p'):
        #     content = content + sele.xpath('./text()').extract()
        # l.add_value('content',content)

        l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td/node()')
        l.add_value('catid',self.catid)

        # l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td')

        # l.add_xpath('content', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//text()')

        d = l.load_item()
        yield d

    def parse_content_item(self, selector):
        pass