# -*- coding: utf-8 -*-
import scrapy
from baby.items import myBaseItem, newsSohuItem, artsoArtronItem
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


class artsoArtronSpider(CrawlSpider):
    # https://news.artron.net//morenews/list732/
    # http: // comment.artron.net / column
    # 艺术家（认证过的）修改自己的简介，可排名提前
    name = 'artso.artron'
    catid = 9
    typeid = 0
    sysadd = 1
    status = 99

    # allowed_domains = ['artist.meishujia.cn'] 国画 书法 油画 雕塑 版画 水粉水彩 当代艺术 当代水墨 漆画
    # cate = ['国画','书法','油画','雕塑','版画','水粉水彩','当代艺术','当代水墨','漆画']
    # start_urls = []
    # for cat in cate:
    #     start_urls.append("http://artso.artron.net/artist/search_artist.php?keyword=&Class="+cat+"&BirthArea=&Graduated=&page=2131")

    # 初始化，手动执行各个分类，增量时使用另一个spider
    cate = '国画'
    start_urls = [
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=国画&BirthArea=&Graduated=&page=2131",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%9B%BD%E7%94%BB&BirthArea=&Graduated=&page=2131",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E4%B9%A6%E6%B3%95&BirthArea=&Graduated=&page=952",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%B2%B9%E7%94%BB&BirthArea=&Graduated=&page=1122",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E9%9B%95%E5%A1%91&BirthArea=&Graduated=&page=244",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E7%89%88%E7%94%BB&BirthArea=&Graduated=&page=237",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%B0%B4%E7%B2%89%E6%B0%B4%E5%BD%A9&BirthArea=&Graduated=&page=138",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%BD%93%E4%BB%A3%E8%89%BA%E6%9C%AF&BirthArea=&Graduated=&page=123",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%BD%93%E4%BB%A3%E6%B0%B4%E5%A2%A8&BirthArea=&Graduated=&page=53",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%BC%86%E7%94%BB&BirthArea=&Graduated=&page=19",
    ]
    # 设置下载延时
    download_delay = 10
    custom_settings = {
        'ITEM_PIPELINES': {
            'baby.pipelines.baseItemPipeline': 210,
            'baby.pipelines.artsoArtistPipeline': 310,
            # 'baby.pipelines.MyImagesPipeline': 410,
            # 'baby.pipelines.MysqlWriterPipeline': 510,
        },
        'DUPEFILTER_DEBUG': True,
        'SCHEDULER_DEBUG': True,
    }
    #不同的start_urls也有不同的rules，
    #从最后一页开始抓，最后一页只能抓一个？
    rules = (
        # 地址分页&page=2 //div[@class="listJump"]/a[last()] xpath未定义first()方法，取第一个用[1] http://artso.artron.net/artist/search_artist.php
        #process_value='process_value'
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="listJump"]'),
                           allow=('\?keyword=&Class=%E5%9B%BD%E7%94%BB&BirthArea=&Graduated=&page=[0-9]+'),),process_links='process_links',follow=True),
        # 详情页 2 /?act=usite&usid=[0-9]{1,10}&inview=[a-z-0-9-]+&said=528  /?act=usite&usid=8646&inview=appid-241-mid-619&said=528
        # process_links='detail_link', ,process_request='parse_request'
        # Rule(LinkExtractor(restrict_xpaths=('//div[@class="listWrap"]//dl//dd//h4//a[last()]')), callback='parse_item'),只能抓取到每页的最后一个
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="listWrap"]//dl//dd//h4'),
                           allow=('/artist/detail.php\?PersonCode=[0-9]+')),process_links='process_item_links',process_request='process_item_request', callback='parse_item'),
    )
    def process_links(self,links):
        # yield links[0]
        print('######')
        print(links)
        print('$$$$$$$')
        for i in range(len(links)-1,-1,-1):
            if links[i].text != '上一页':
                del links[i]
        print(links)
        print('@@@@@@')
        return links

    def process_item_request(self,request):
        print('333333333333')
        print(request)
        print('4444444444444')
        return request
        pass
    def process_item_links(self,links):
        # yield links[0]
        print('22222222######')
        print(links)
        print('22222222$$$$$$$')
        return links

    def process_value(value):
        m = re.search("上一页", value)
        if m:
            m1 = re.search('<a href="(.+?)">',value)
            if m1:
                return m1.group(1)
        print(value)
        pass

    # def start_requests(self):
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%9B%BD%E7%94%BB&BirthArea=&Graduated=&page=2131",self.parse)
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E4%B9%A6%E6%B3%95&BirthArea=&Graduated=&page=952",self.parse)
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%B2%B9%E7%94%BB&BirthArea=&Graduated=&page=1122", self.parse)
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E9%9B%95%E5%A1%91&BirthArea=&Graduated=&page=244", self.parse)
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E7%89%88%E7%94%BB&BirthArea=&Graduated=&page=237", self.parse)
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%B0%B4%E7%B2%89%E6%B0%B4%E5%BD%A9&BirthArea=&Graduated=&page=138", self.parse)
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%BD%93%E4%BB%A3%E8%89%BA%E6%9C%AF&BirthArea=&Graduated=&page=123", self.parse)
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%BD%93%E4%BB%A3%E6%B0%B4%E5%A2%A8&BirthArea=&Graduated=&page=53", self.parse)
    #     yield scrapy.Request("http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%BC%86%E7%94%BB&BirthArea=&Graduated=&page=19", self.parse)
    #
    # def parse(self, response):
    #     base_url = get_base_url(response)
    #     url_parse = urlparse(base_url)
    #     query = parse_qs(url_parse.query)
    #     self.cate=query['Class'][0]

    def parse_item(self, response):
        # self.state['items_count'] = self.state.get('items_count', 0) + 1
        # http://blog.51cto.com/pcliuyang/1543031
        l = DefaultItemLoader(item=artsoArtronItem(), selector=response)
        base_url = get_base_url(response)
        urls = urlparse(base_url)
        query = parse_qs(urls.query)
        # print(base_url)
        l.add_value('spider_link', base_url)
        l.add_xpath('title', 'normalize-space(//dd[re:test(@class,"poR")]//h3/text())')

        # 可能没有 click，如果返回2个则取第2个，否则取第1个。
        content = response.xpath('//dd//div[re:test(@class,"artTxt click")]//p//node()')
        if len(content) > 0:
            l.add_xpath('spider_content', '//dd//div[re:test(@class,"artTxt click")]//p//node()')
        else:
            l.add_xpath('spider_content', '//dd//div[re:test(@class,"artTxt")]//p//node()')
        l.add_value('keywords', '')
        l.add_value('description', '')
        # css
        # l.add_css('spider_img', 'dl dt .pic img::attr(src)')
        # xpath
        l.add_xpath('spider_img', '//dl//dt//div[re:test(@class,"pic")]//img/@src')
        l.add_value('spider_imgs', [])
        l.add_value('thumbs', [])
        l.add_value('spider_userpic', '')
        l.add_value('spider_tags', [self.cate])
        l.add_value('uid', 0)
        l.add_value('uname', '')
        # 生成文章id
        l.add_value('aid', util.genId(type="artist", def_value=int(query['PersonCode'][0])))
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
