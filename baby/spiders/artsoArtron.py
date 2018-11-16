# -*- coding: utf-8 -*-
import scrapy
from baby.items import artistMeishujiaItem,newsSohuItem

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
class artsoArtronSpider(CrawlSpider):
    #https://news.artron.net//morenews/list732/
    # http: // comment.artron.net / column
    #艺术家（认证过的）修改自己的简介，可排名提前
    name = 'artso.artron'
    catid=6
    typeid=0
    sysadd=1
    status=99

    # allowed_domains = ['artist.meishujia.cn'] 国画 书法 油画 雕塑 版画 水粉水彩 当代艺术 当代水墨 漆画
    start_urls = ["http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%9B%BD%E7%94%BB&BirthArea=&Graduated=2131"]
    # 设置下载延时
    download_delay = 10
    custom_settings = {
        'ITEM_PIPELINES': {
                    'baby.pipelines.artPipeline': 300,
                    # 'baby.pipelines.MyImagesPipeline': 400,
                    # 'baby.pipelines.MysqlWriterPipeline': 500,
        },

    }
    rules = (
        # 地址分页&page=2
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="listJump"]')),process_links='page_link'),
        # 详情页1
        # Rule(LinkExtractor(restrict_xpaths=('//li[@class="i42c"]/div[@class="i42ck"]'))),
        # 详情页 2 /?act=usite&usid=[0-9]{1,10}&inview=[a-z-0-9-]+&said=528  /?act=usite&usid=8646&inview=appid-241-mid-619&said=528
        Rule(LinkExtractor(restrict_xpaths=('//dl/dd/h4')),process_links='detail_link',callback='parse_item')
    )
    def page_link(self,links):
        print(links[0])
        yield links[0]

    def detail_link(self,links):
        print(links[0])
        yield links[0]

    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=newsSohuItem(),selector=response)
        l.add_value('spider_link', get_base_url(response))
        # l.add_xpath('spider_img', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[1]/td/img::attr(src)')
        l.add_xpath('title', 'normalize-space(//dd[re:test(@class,"poR")]//h3/text())')
        # normalize-space 去除 html \r\n\t
        # re 正则表达式，class只要包含theme_body_4656
        # l.add_xpath('content', 'normalize-space(//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td)')
        # content=""for selector in sel.xpath('//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//p'): content=content+ selector.xpath("/text()").extract()

        # for sele in response.xpath('//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//p'):
        #     content = content + sele.xpath('./text()').extract()
        # l.add_value('content',content)
        #可能没有 click，如果返回2个则取第2个，否则取第1个。
        l.add_xpath('content', '//dd//div[re:test(@class,"artTxt")]//p//node()')
        l.add_value('keywords', '')
        l.add_value('description', '')

        #css
        #l.add_css('spider_img', 'dl dt .pic img::attr(src)')
        #xpath
        l.add_xpath('spider_img', '//dl//dt//div[re:test(@class,"pic")]//img/@src')

        l.add_value('spider_imgs', '')
        l.add_value('thumbs', '')

        l.add_value('catid',self.catid)
        l.add_value('status', self.status)
        l.add_value('sysadd', self.sysadd)
        l.add_value('typeid', self.typeid)
        l.add_value('inputtime',int(time.time()))
        l.add_value('updatetime', int(time.time()))
        l.add_value('create_time',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        l.add_value('update_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        d = l.load_item()
        yield d

    def parse_content_item(self, selector):
        pass