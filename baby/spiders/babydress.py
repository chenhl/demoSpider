# -*- coding: utf-8 -*-
import logging
import scrapy
from baby.items import BabyItem,BabyDetailItem
from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor

from urllib.parse import urlsplit,urlparse,urljoin
#item loader
class DefaultItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

'''
CrawlSpider。都知道在写自己的spider的时候需要继承scrapy的spider，除了scrapy.Spider外，scrapy还提供了好几种spider，其中CrawlSpider算是比较常用的。
CrawlSpider的优势在于可以用rules方便地规定新的url的样子，即通过正则匹配来约束url。并且不需要自己生成新的url，
CrawlSpider会自己寻找源码中所有符合要求的新url的。另外，rules的回调方法名字最好不要叫parse。
'''
class BabydressSpider(CrawlSpider):
    name = 'babydress'
    # 设置下载延时
    download_delay = 1
    custom_settings = {
        'ITEM_PIPELINES': {
            'baby.pipelines.BabyPipeline': 300,
            # 'baby.pipelines.JsonWriterPipeline': 350,
            # 'baby.pipelines.MultiImagesPipeline': 400,
            # 'baby.pipelines.MysqlWriterPipeline': 500,
        },
    }
    allowed_domains = ['babyonlinewholesale.com']
    start_urls = ['https://www.babyonlinewholesale.com/wedding-dresses-c1']
    rules = (
        # # 导航地址
        # Rule(LinkExtractor(allow=('[a-z-0-9]-c\d+'),allow_domains=('www.babyonlinewholesale.com'),
        #                    restrict_xpaths=('//div[@class="nav-box"]'),unique=False)),
        # 导航地址分页
        Rule(LinkExtractor(allow=('[a-z-0-9]-c\d+/page-\d+'),restrict_xpaths=('//div[@class="paging fr"]/a[last()]'))),
        #详情页
        # Rule(LinkExtractor(allow=('[a-z-0-9]-g\d+'),process_links='process_links',callback='parse_item')),
        Rule(LinkExtractor(allow=('[a-z-0-9]-g\d+'),restrict_xpaths=('//div[re:test(@class,"clothing-item")]/a')), process_links='parse_links', callback='parse_item'),
    )
    def parse_links(self,links):
        # ret = []
        for link in links:
           # print('---------')
           # print(link)
           # print(type(link))
           # print('---------')
           u = urlparse(link.url)
           # print(u)
           u_new = urljoin('http://www.babyonlinewholesale.com/',u.path)
           # print(u_new)
           link.url=u_new
           yield link
           # ret.append(u_new)
        # return ret
     # pass
    # def start_requests(self):
    #
    #     pass
    def parse_item(self, response):
        l = DefaultItemLoader(item=BabyDetailItem(),selector=response)
        l.add_value('cur_link', get_base_url(response))
        l.add_xpath('name', '/html/head/title/text()')
        d = l.load_item()
        yield d


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
