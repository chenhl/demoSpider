# -*- coding: utf-8 -*-
import scrapy
from baby.items import myBaseItem,newsSohuItem
from baby.util.util import util
from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit,urlparse,urljoin,parse_qs,parse_qsl
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
    name = 'exhibit.artron'
    catid=10
    typeid=0
    sysadd=1
    status=99
    # 初始化
    start_urls = [
        "http://artso.artron.net/exhibit/search_exhibition.php?page=5674",
    ]
    # 设置下载延时
    download_delay = 10
    custom_settings = {
        'ITEM_PIPELINES': {
                    'baby.pipelines.artsoExhibitPipeline': 320,
                    # 'baby.pipelines.MyImagesPipeline': 420,
                    # 'baby.pipelines.MysqlWriterPipeline': 520,
        },
    }
    rules = (
        #分页
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="result-page"]/a[2]'))),
        # 详情页
        #process_links='detail_link',
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="show_list"]//dl/dt/a[1]')), cb_kwargs={}, process_links='parse_links', callback='parse_item')
    )

    def parse_links(self, links):
        # ret = []
        for link in links:
            u = urlparse(link.url)
            qs = parse_qs(u.query)
            link.url = qs['url'][0]
            yield link
    # def parse(self, response):
    #     base_url = get_base_url(response)
    #     url_parse = urlparse(base_url)
    #     query = parse_qs(url_parse.query)
    #     self.cate=query['Class'][0]

    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=newsSohuItem(),selector=response)
        base_url = get_base_url(response)
        urls = urlparse(base_url)
        query = parse_qs(urls.query)

        l.add_value('spider_link', base_url)
        # l.add_xpath('spider_img', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[1]/td/img::attr(src)')
        l.add_xpath('title', 'normalize-space(//div[re:test(@class,"pw fix exDetail")]//h1/text())')
        # normalize-space 去除 html \r\n\t
        # re 正则表达式，class只要包含theme_body_4656
        # l.add_xpath('content', 'normalize-space(//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td)')
        # content=""for selector in sel.xpath('//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//p'): content=content+ selector.xpath("/text()").extract()

        # for sele in response.xpath('//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//p'):
        #     content = content + sele.xpath('./text()').extract()
        # l.add_value('content',content)

        #content
        l.add_xpath('spider_content', '//div[re:test(@class,"exText")]//node()')
        l.add_value('keywords', '')
        l.add_value('description', '')

        #css
        #l.add_css('spider_img', 'dl dt .pic img::attr(src)')
        #
        l.add_xpath('spider_img', '')
        l.add_value('spider_imgs', '//div[re:test(@class,"imgnav")]//img/@src')
        l.add_value('spider_imgs_text', 'normalize-space(//div[re:test(@class,"imgnav")]//span/text())')
        l.add_value('thumbs', [])
        l.add_value('spider_userpic', '')
        l.add_value('spider_tags', [])

        l.add_value('uid', 0)
        l.add_value('uname', '')
        #生成文章id
        l.add_value('aid', util.genId(type="artist",def_value=int(query['PersonCode'][0])))

        # tags = [self.cate]
        # l.add_value('tags', tags)

        l.add_value('spider_name', self.name)
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