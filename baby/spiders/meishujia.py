# -*- coding: utf-8 -*-
import scrapy


class MeishujiaSpider(scrapy.Spider):
    name = 'meishujia'
    allowed_domains = ['meishujia.cn']
    start_urls = ['http://meishujia.cn/']

    def parse(self, response):
        pass
