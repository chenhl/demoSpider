# -*- coding: utf-8 -*-
import scrapy
from baby.items import galleryArtronItem
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
#D:/apps/baby/baby
#f:/baby/scrapy/demoSpider/baby
# scrapy crawl gallery.artron -s JOBDIR=D:/xampp7/scrapy/crawls/gallery_artron
class galleryArtronSpider(CrawlSpider):
    # https://news.artron.net//morenews/list732/
    # http: // comment.artron.net / column
    name = 'gallery.artron'
    catid = 11
    typeid = 0
    sysadd = 1
    status = 99
    uid = 98657
    uname = '艺术画廊'
    # 初始化
    start_urls = [
        "http://gallery.artron.net/class/0-0-0-1.html?order=4",
    ]
    # 设置下载延时
    download_delay = 10
    custom_settings = {
        'ITEM_PIPELINES': {
            'baby.pipelines.baseItemPipeline': 220,
            'baby.pipelines.galleryPipeline': 320,
            'baby.pipelines.MyImagesPipeline': 420,
            'baby.pipelines.MysqlWriterPipeline': 520,
        },
        'DUPEFILTER_DEBUG': True,
        'SCHEDULER_DEBUG': True,
        'LOG_FILE': 'logs/log-gallery.txt',
        'LOG_LEVEL': 'INFO',
    }

    # start_urls parse
    def parse(self, response):
        base_url = 'http://gallery.artron.net'
        # list url
        sels_url = get_base_url(response)
        sels_url_parse = urlparse(sels_url)
        sels_url_path = sels_url_parse.path
        # next page
        page = int(sels_url_path.split('-')[-1].split('.')[0]) + 1
        page_url = base_url + '/class/0-0-0-' + str(page) + '.html?order=4'
        # print(page_url)
        self.logger.info(page_url)
        yield scrapy.Request(page_url, dont_filter=False)

        # item
        sels = response.xpath('//div[@class="shop"]//div[@class="shopList"]')
        for sel in sels:
            # +'/g_infor1584.html'
            url = sel.xpath('./h3/a/@href').extract()[0]
            p = urlparse(url)
            # id
            item_id = p.path.strip('/')
            # url
            item_url = url + '/g_infor' + item_id + '.html'
            # 名称
            title = sel.xpath('./h3/a/text()').extract()[0]
            # 属性
            attrs = sel.xpath('./dl//dd//td[2]')
            attr_key = {}
            for attr in attrs:
                _tmp = attr.xpath('./p')
                #所在城市
                _tmp_attr = _tmp[0].xpath('./span/text()').extract()[0]
                _tmp_value = _tmp[0].xpath('./b/text()').extract()
                attr_key[_tmp_attr] = _tmp_value
                #主营项目
                _tmp_attr = _tmp[1].xpath('./span/text()').extract()[0]
                _tmp_value = _tmp[1].xpath('./b/text()').extract()
                attr_key[_tmp_attr] = _tmp_value

            meta = {'item_id': item_id, 'item_url': item_url, 'title': title, 'attr': attr_key}
            self.logger.info(item_url)
            yield scrapy.Request(item_url, callback=self.parse_item, meta=meta, dont_filter=False)

    def parse_item(self, response):
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=galleryArtronItem(), selector=response)
        base_url = get_base_url(response)
        urls = urlparse(base_url)
        query = parse_qs(urls.query)
        l.add_value('spider_link', base_url)
        l.add_value('title', response.meta['title'])

        # attr
        l.add_value('spider_attr', response.meta['attr'])
        l.add_value('attr', {})
        l.add_value('attr_value', [])
        # content
        # 简介
        contents1 = response.xpath('//div[re:test(@class,"tabsCont")]')[0].xpath('./node()').extract()
        # 风采
        contents2 = response.xpath('//div[re:test(@class,"tabsCont")]')[2].xpath('./node()').extract()
        # 联系
        contents3 = response.xpath('//div[re:test(@class,"tabsCont")]')[4].xpath('./node()').extract()
        l.add_value('spider_content', contents1)
        l.add_value('spider_content2', contents2)

        contents_linkus = response.xpath('//div[re:test(@class,"tabsCont")]//div[re:test(@class,"contact")]//span')
        linkus = {}
        if len(contents_linkus) == 5:
            linkus['man'] = contents_linkus[0].xpath('./text()').extract()
            linkus['address'] = contents_linkus[1].xpath('./text()').extract()
            linkus['phone'] = contents_linkus[2].xpath('./text()').extract()
            linkus['phone1'] = contents_linkus[3].xpath('./text()').extract()
            linkus['email'] = contents_linkus[4].xpath('./text()').extract()
        l.add_value('linkus', linkus)

        l.add_value('keywords', '')
        l.add_value('description', '')

        l.add_xpath('spider_img', '//div[re:test(@class,"imgWrap")]//img/@src')
        l.add_value('spider_imgs', [])
        l.add_value('spider_imgs_text', [])
        l.add_value('thumbs', [])
        l.add_value('spider_userpic', '')
        l.add_value('spider_tags', [])

        l.add_value('uid', self.uid)
        l.add_value('uname', self.uname)
        # 生成文章id
        l.add_value('aid', util.genId(type="gallery", def_value=int(response.meta['item_id'])))
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
