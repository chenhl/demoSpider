# -*- coding: utf-8 -*-
import scrapy
from baby.items import BabyItem,BabyDetailItem
from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
#item loader
class DefaultItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class BabydressSpider(CrawlSpider):
    name = 'babydress'
    allowed_domains = ['babyonlinedress.cn']
    # accessories - c147 /
    start_urls = ['http://www-test.babyonlinedress.cn/']
    rules = (
        Rule(LinkExtractor(allow=('http://www-test.babyonlinedress.cn/-c\d'))),
        Rule(LinkExtractor(allow=('http://www-test.babyonlinedress.cn/-g\d')),callback='pass_item')
    )
    def parse_item(self, response):
        infos1 = response.css('div.clothing-item')
        for info in infos1:
            l = DefaultItemLoader(item=BabyDetailItem(),selector=info)
            l.add_value('cur_link', get_base_url(response))
            l.add_css('name', '/html/head/title')
            # print(l.load_item())
            yield l.load_item()


    def parse1(self, response):
        infos1 = response.css('div.clothing-item')
        for info in infos1:
            l = DefaultItemLoader(item=BabyItem(),selector=info)
            l.add_value('cur_link', get_base_url(response))
            l.add_css('name', 'div.clothing-info p.clothing-name::text')
            l.add_xpath('image_urls', 'a/img/@data-original')
            l.add_css('shop_price', 'div.clothing-info span.price-small b::text')
            l.add_css('market_price', 'div.clothing-info span.price-big b::text')
            # print(l.load_item())
            yield l.load_item()
    def parse3(self, response):
        css = 'div.clothing-item div.clothing-info '

        l = ItemLoader(item=BabyItem(), response=response)
        l.add_value('cur_link', get_base_url(response))
        l.add_css('name', css + 'p.clothing-name::text')
        l.add_css('shop_price', css + 'span.price-small b::text')
        l.add_css('market_price', css + 'span.price-big b::text')
        return l.load_item()

    def parse2(self, response):
        infos = response.css('div.clothing-item div.clothing-info')
        items = []
        for info in infos:
            item = BabyItem()
            item['cur_link'] = get_base_url(response)
            item['name'] = info.css('p.clothing-name::text').extract()[0]
            item['image_url'] = info.css('a img::attr(src)::text').extract()[0]
            item['shop_price'] = info.css('span.price-small b::text').extract()[0]
            item['market_price'] = info.css('span.price-big b::text').extract()[0]
            items.append(item)
            # print(item)
            yield item
        # return items
