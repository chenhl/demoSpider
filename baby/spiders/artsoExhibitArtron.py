# -*- coding: utf-8 -*-
import scrapy
from baby.items import myBaseItem, newsSohuItem, exhibitArtronItem
from baby.util.util import util
from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit, urlparse, urljoin, parse_qs, parse_qsl
import time
import datetime
import re
from selenium import webdriver
from scrapy import signals
#弃用
# from scrapy.xlib.pydispatch import dispatcher

# item loader
class DefaultItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    pass
#D:/apps/baby/baby
#f:/baby/scrapy/demoSpider/baby
#scrapy crawl exhibit.artron -s JOBDIR=D:/xampp7/scrapy/crawls/exhibit_artron00
class artsoExhibitArtronSpider(CrawlSpider):
    # https://news.artron.net//morenews/list732/
    # http: // comment.artron.net / column
    # 艺术家（认证过的）修改自己的简介，可排名提前
    name = 'exhibit.artron'
    catid = 10
    typeid = 0
    sysadd = 1
    status = 99
    uid = 70
    uname = '艺术展览'

    # 初始化
    start_urls = [
        "http://artso.artron.net/exhibit/search_exhibition.php?page=542",
    ]
    # 设置下载延时
    download_delay = 10
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # 'baby.middlewares.artsoExhibitSeleniumMiddleware': 10,
            'scrapy_crawlera.CrawleraMiddleware': 50,
            'baby.middlewares.RandomUserAgent': 100,
        },
        'ITEM_PIPELINES': {
            'baby.pipelines.baseItemPipeline': 220,
            'baby.pipelines.itemExistsPipeline': 260,
            'baby.pipelines.artsoExhibitPipeline': 320,
            'baby.pipelines.MyImagesPipeline': 420,
            'baby.pipelines.MysqlWriterPipeline': 520,
        },
        'DUPEFILTER_DEBUG': True,
        'SCHEDULER_DEBUG': True,
        'LOG_FILE':'logs/log-exhibit00.txt',
        'LOG_LEVEL':'INFO',
        'IMAGES_MIN_WIDTH':20,
        'IMAGES_MIN_HEIGHT':20,
    }

    # @classmethod
    # def from_crawler(cls,crawler, *args, **kwargs):
    #     spider = super(artsoExhibitArtronSpider, cls).from_crawler(crawler, *args, **kwargs)
    #     # spider启动信号和spider_opened函数绑定
    #     crawler.signals.connect(spider.spider_opened, signals.spider_opened)
    #     # spider关闭信号和spider_spider_closed函数绑定
    #     crawler.signals.connect(spider.spider_closed, signals.spider_closed)
    #     return spider
    #
    # def spider_opened(self, spider):
    #     print("spider opened")
    #     self.browser = webdriver.Firefox()
    #     self.browser.set_page_load_timeout(30)
    #
    # def spider_closed(self, spider):
    #     print("spider closed")
    #     self.browser.close()

    # def __init__(self, *args, **kwargs):
    #     print("spider opened")
    #     self.browser = webdriver.Firefox("D:/firefox/")
    #     self.browser.set_page_load_timeout(30)
    #
    # def closed(self, spider):
    #     print("spider closed")
    #     self.browser.close()

    # list_arg = {}
    rules = (
        # 地址分页,callback='parse_list'
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="result-page"]'),
                           allow=('/exhibit/search_exhibition.php\?page=[0-9]+'), ), process_links='process_links',
             follow=True),
        # 详情页 ,cb_kwargs={}
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="show_list"]//dl//dt'), ), process_links='process_item_links',
             callback='parse_item'),
    )

    # 列表页上一页的url
    def process_links(self, links):
        for i in range(len(links) - 1, -1, -1):
            if links[i].text != '< 上一页':
                del links[i]
        self.logger.info(links)
        return links

    # def process_item_request(self, request):
    #     return request

    def process_item_links(self, links):
        # yield links[0]
        for i in range(len(links)):
            u = urlparse(links[i].url)
            qs = parse_qs(u.query)
            links[i].url = qs['url'][0]

        self.logger.info(links)

        return links

    # def parse_list(self, response):
    #     list_imgs = response.xpath('//div[@class="show_list"]//dl//dt//img/@src')
    #     pass
    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=exhibitArtronItem(), selector=response)
        base_url = get_base_url(response)
        self.logger.info(base_url)
        urls = urlparse(base_url)
        query = parse_qs(urls.query)

        l.add_value('spider_link', base_url)
        # l.add_xpath('spider_img', '//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[1]/td/img::attr(src)')
        l.add_xpath('title', 'normalize-space(//div[re:test(@class,"pw fix exDetail")]//h1/text())')
        # normalize-space 去除 html \r\n\t
        # re 正则表达式，class只要包含theme_body_4656
        # l.add_xpath('content', 'normalize-space(//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td)')
        # content=""for selector in sel.xpath('//dd[re:test(@class,"theme_body_4656")]//table[2]//tr[3]/td//p'): content=content+ selector.xpath("/text()").extract()

        # list 索引顺序
        # attr = []
        # value = []
        # for sele in response.xpath('//div[re:test(@class,"exInfo")]/dl'):
        #     attr.append(sele.xpath('./dt//text()').extract()[0])
        #     value.append(sele.xpath('./dd//text()').extract())
        attr = {}
        # value = []
        for sele in response.xpath('//div[re:test(@class,"exInfo")]/dl'):
            _attr = sele.xpath('./dt//text()').extract()[0]
            _val = sele.xpath('./dd//text()').extract()
            attr[_attr]=_val
        # attr
        l.add_value('spider_attr', attr)
        l.add_value('attr', {})
        l.add_value('attr_value', [])
        # content
        l.add_xpath('spider_content', '//div[re:test(@class,"exText")]//node()')
        l.add_value('keywords', '')
        l.add_value('description', '')

        l.add_value('spider_img', '')
        #images
        images = []
        for sele in response.xpath('//div[re:test(@class,"imgnav")]//div[re:test(@id,"img")]//ul/li'):
            img = {}
            _img = sele.xpath('.//img/@src').extract()[0]
            _txt = sele.xpath('./span/text()').extract()
            img['img'] = _img
            img['txt'] = _txt
            images.append(img)
            pass
        l.add_value('spider_imgs', [])
        l.add_value('spider_imgs_text', images)
        # l.add_xpath('spider_imgs', '//div[re:test(@class,"imgnav")]//div[re:test(@id,"img")]//ul/li//img/@src')
        # l.add_xpath('spider_imgs_text', '//div[re:test(@class,"imgnav")]//div[re:test(@id,"img")]//ul/li/span/text()')
        l.add_value('thumbs', [])
        l.add_value('spider_userpic', '')
        l.add_value('spider_tags', [])

        l.add_value('uid', self.uid)
        l.add_value('uname', self.uname)
        # 生成文章id
        l.add_value('aid', util.genId(type="exhibit", def_value=int(base_url.split('-')[1].split('.')[0])))
        l.add_value('spider_name', self.name)
        l.add_value('catid', self.catid)
        l.add_value('status', self.status)
        l.add_value('sysadd', self.sysadd)
        l.add_value('typeid', self.typeid)
        l.add_value('inputtime', int(time.time()))
        l.add_value('updatetime', int(time.time()))
        l.add_value('create_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        l.add_value('update_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        d = l.load_item()
        yield d

    def parse_content_item(self, selector):
        pass
