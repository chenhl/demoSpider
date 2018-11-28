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


# item loader
class DefaultItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    pass

#scrapy crawl gallery.artron -s JOBDIR=crawls/gallery_artron
class galleryArtronSpider(CrawlSpider):
    # https://news.artron.net//morenews/list732/
    # http: // comment.artron.net / column
    # 艺术家（认证过的）修改自己的简介，可排名提前
    name = 'gallery.artron'
    catid = 10
    typeid = 0
    sysadd = 1
    status = 99
    # 初始化
    start_urls = [
        "http://gallery.artron.net/class/0-0-0-1.html?order=4",
    ]
    # 设置下载延时
    download_delay = 10
    custom_settings = {
        'ITEM_PIPELINES': {
            'baby.pipelines.baseItemPipeline': 220,
            # 'baby.pipelines.artsoExhibitPipeline': 320,
            # 'baby.pipelines.MyImagesPipeline': 420,
            # 'baby.pipelines.MysqlWriterPipeline': 520,
        },
        'DUPEFILTER_DEBUG': True,
        'SCHEDULER_DEBUG': True,
        'LOG_FILE':'logs/log-gallery.txt',
        'LOG_LEVEL':'INFO',
    }

    # start_urls parse
    def parse(self, response):
        base_url = 'http://gallery.artron.net'
        # list url
        sels_url = get_base_url(response)
        sels_url_parse = urlparse(sels_url)
        sels_url_path = sels_url_parse.path
        # next page
        # pages = response.xpath('//div[@class="listJump"]')
        page = int(sels_url_path.split('-')[-1].split('.')[0]) + 1
        page_url = base_url + '/class/0-0-0-' + str(page)+'.html?order=4'
        # print(page_url)
        self.logger.info(page_url)
        yield scrapy.Request(page_url, dont_filter=False)

        # item
        sels = response.xpath('//div[@class="shop"]//div[@class="shopList"]')
        for sel in sels:
            url = base_url + sel.xpath('./h3/a/@href').extract()[0]
            title = sel.xpath('./h3/a/text()').extract()[0]
            img = sel.xpath('./dl/dt/img/@src').extract()[0]
            meta = {'cate': ''}
            self.logger.info(url + ',meta=' + meta['cate'])
            yield scrapy.Request(url, callback=self.parse_item, meta=meta, dont_filter=False)
            # print(url+'&cate='+meta['cate'])

    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=exhibitArtronItem(), selector=response)
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

        # list 索引顺序
        attr = []
        value = []
        for sele in response.xpath('//div[re:test(@class,"exInfo")]/dl'):
            attr.append(sele.xpath('./dt//text()').extract()[0])
            value.append(sele.xpath('./dd//text()').extract())
        # attr
        l.add_value('attr', attr)
        l.add_value('attr_value', value)
        # content
        l.add_xpath('spider_content', '//div[re:test(@class,"exText")]//node()')
        l.add_value('keywords', '')
        l.add_value('description', '')

        l.add_value('spider_img', '')
        l.add_xpath('spider_imgs', '//div[re:test(@class,"imgnav")]//div[re:test(@id,"img")]//ul/li//img/@src')
        l.add_xpath('spider_imgs_text', '//div[re:test(@class,"imgnav")]//div[re:test(@id,"img")]//ul/li/span/text()')
        l.add_value('thumbs', [])
        l.add_value('spider_userpic', '')
        l.add_value('spider_tags', [])

        l.add_value('uid', 0)
        l.add_value('uname', '')
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
