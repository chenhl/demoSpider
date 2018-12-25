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
#D:/apps/baby/baby
#f:/baby/scrapy/demoSpider/baby
#scrapy crawl artist.artron -s JOBDIR=D:/xampp7/scrapy/crawls/artist_artron8
class artsoArtistArtronSpider(CrawlSpider):
    # https://news.artron.net//morenews/list732/
    # http: // comment.artron.net / column
    # 艺术家（认证过的）修改自己的简介，可排名提前
    name = 'artist.artron'
    catid = 9
    typeid = 0
    sysadd = 1
    status = 99
    uid = 80
    uname = '艺术人物'
    # allowed_domains = ['artist.meishujia.cn'] 国画 书法 油画 雕塑 版画 水粉水彩 当代艺术 当代水墨 漆画
    # cate = ['国画','书法','油画','雕塑','版画','水粉水彩','当代艺术','当代水墨','漆画']
    # start_urls = []
    # for cat in cate:
    #     start_urls.append("http://artso.artron.net/artist/search_artist.php?keyword=&Class="+cat+"&BirthArea=&Graduated=&page=2131")

    # 初始化，手动执行各个分类，增量时使用另一个spider
    # cate = '国画'
    start_urls = [
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=国画&BirthArea=&Graduated=&page=198",
        "http://artso.artron.net/artist/search_artist.php?keyword=&Class=书法&BirthArea=&Graduated=&page=853",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=油画&BirthArea=&Graduated=&page=1126",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=雕塑&BirthArea=&Graduated=&page=244",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=版画&BirthArea=&Graduated=&page=237",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=水粉水彩&BirthArea=&Graduated=&page=138",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=当代艺术&BirthArea=&Graduated=&page=124",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=当代水墨&BirthArea=&Graduated=&page=53",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=漆画&BirthArea=&Graduated=&page=19",

        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%9B%BD%E7%94%BB&BirthArea=&Graduated=&page=2131",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E4%B9%A6%E6%B3%95&BirthArea=&Graduated=&page=952",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%B2%B9%E7%94%BB&BirthArea=&Graduated=&page=1122",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E9%9B%95%E5%A1%91&BirthArea=&Graduated=&page=244",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E7%89%88%E7%94%BB&BirthArea=&Graduated=&page=237",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%B0%B4%E7%B2%89%E6%B0%B4%E5%BD%A9&BirthArea=&Graduated=&page=138",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%BD%93%E4%BB%A3%E8%89%BA%E6%9C%AF&BirthArea=&Graduated=&page=123",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E5%BD%93%E4%BB%A3%E6%B0%B4%E5%A2%A8&BirthArea=&Graduated=&page=53",
        # "http://artso.artron.net/artist/search_artist.php?keyword=&Class=%E6%BC%86%E7%94%BB&BirthArea=&Graduated=&page=19",
    ]
    # 设置下载延时
    download_delay = 18
    custom_settings = {
        'ITEM_PIPELINES': {
            'baby.pipelines.baseItemPipeline': 210,
            'baby.pipelines.artsoArtistPipeline': 310,
            'baby.pipelines.MyImagesPipeline': 410,
            'baby.pipelines.MysqlUpdatePipeline': 510,
        },
        'DUPEFILTER_DEBUG': True,
        'SCHEDULER_DEBUG': True,
        'LOG_FILE': 'logs/log-artist8.txt',
        'LOG_LEVEL': 'INFO',
    }
    #不同的start_urls也有不同的rules，
    # 精抓取，详情页需要列表页的参数（self.cate），没有找到好的方法，不用rules
    # rules = (
    #     # 地址分页
    #     Rule(LinkExtractor(restrict_xpaths=('//div[@class="listJump"]'),
    #                        allow=('\?keyword=&Class=%E5%9B%BD%E7%94%BB&BirthArea=&Graduated=&page=[0-9]+'),),process_links='process_links',follow=True),
    #     # 详情页
    #     Rule(LinkExtractor(restrict_xpaths=('//div[@class="listWrap"]//dl//dd//h4'),
    #                        allow=('/artist/detail.php\?PersonCode=[0-9]+')),process_links='process_item_links',process_request='process_item_request', callback='parse_item'),
    # )

    #start_urls parse
    def parse(self, response):
        base_url = 'http://artso.artron.net'
        #list url
        sels_url = get_base_url(response)
        sels_url_parse = urlparse(sels_url)
        sels_url_query = parse_qs(sels_url_parse.query)
        #next page
        # pages = response.xpath('//div[@class="listJump"]')
        page = int(sels_url_query['page'][0])-1
        if page > 0:
            # query = {'keyword':'','Class':sels_url_query['Class'][0],'Graduated':'','page':page}
            query = 'keyword=&Class=' + sels_url_query['Class'][0] + '&BirthArea=&Graduated=&page=' + str(page)
            page_url = base_url + '/artist/search_artist.php?' + query
            # print(page_url)
            self.logger.info(page_url)
            yield scrapy.Request(page_url, dont_filter=False)

        # item
        sels = response.xpath('//div[@class="listWrap"]//dl//dd//h4//a[last()]')
        for sel in sels:
            url = base_url+sel.xpath('./@href').extract()[0]
            meta = {'cate': sels_url_query['Class'][0]}
            #scrapy 默认使用url去重，artist可能属于多个分类，在此url加上分类信息可以多次爬取合并多个分类信息
            url = url + '&cate='+meta['cate']
            self.logger.info(url+',meta='+meta['cate'])
            yield scrapy.Request(url, callback=self.parse_item, meta=meta, dont_filter=False)
            # print(url+'&cate='+meta['cate'])

    #https://github.com/aleonsan/newspaper-scraper-couchbase/blob/master/newspaper_crawler.py
    # def __init__(self, *args, **kwargs):
    #
    #     pass

    # def parse_start_url(self,response):
    #     return []

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
        l.add_value('spider_tags', [response.meta['cate']])

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
        l.add_value('uid', self.uid)
        l.add_value('uname', self.uname)
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
