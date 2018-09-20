# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import logging
from scrapy.exceptions import DropItem
import scrapy
from scrapy.pipelines.images import ImagesPipeline
import hashlib
from urllib.parse import quote, urlparse
import pymysql
# 导入项目设置
from scrapy.utils.project import get_project_settings
# 导入这个包为了移动文件
import shutil
# 这个包不解释
import os
import time
import pymongo


class BabyPipeline(object):
    def process_item(self, item, spider):
        pass
        # if float(item['shop_price']) > 10.0:
        #     return item
        # else:
        #     raise DropItem("Missing price in %s" % item)


class exhibitPipeline(object):
    # 在你的多少范围内有展览
    meta = ['展览名称：', '展览时间：', '展览地点：', '主办单位：', '参展艺术家：']
    meta2 = [{'txt': '展览名称：', 'code': 'name'}, {'txt': '展览时间：', 'code': 'time'}, {'txt': '展览地点：', 'code': 'area'},
             {'txt': '主办单位：', 'code': 'company'}, {'txt': '参展艺术家：', 'code': 'artists'}]

    def process_item(self, item, spider):
        print(item['attr'])
        print(type(item['attr']))
        print(len(item['attr']))

        i = 0
        max = len(self.meta) - 1
        res = []
        for data_meta in self.meta2:
            _index = item['attr'].index(data_meta['txt'])
            if i < max:
                _next_index = item['attr'].index(self.meta[i + 1])
                _tmp = {'attr': data_meta['code'], 'attr_txt': data_meta['txt'],
                        'value': item['attr'][_index + 1:_next_index]}
            else:
                _tmp = {'attr': data_meta['code'], 'attr_txt': data_meta['txt'],
                        'value': item['attr'][_index + 1:_index + 2]}

            # 时间范围处理
            if data_meta['code'] == 'time':
                _times = _tmp['value'].split('~')
                time_struct_start = time.strptime(_times[0], '%Y%m/%d')
                time_struct_end = time.strptime(_times[1], '%Y%m/%d')
                str_time_start = time.strftime('%Y-%m-%d %H:%M:%S', time_struct_start)
                str_time_end = time.strftime('%Y-%m-%d %H:%M:%S', time_struct_end)
            # 地点处理
            if data_meta['code'] == 'area':
                pass

            res.append(_tmp)
            i = i + 1

        item['attr_value'] = res
        return item


class artPipeline(object):
    def process_item(self, item, spider):
        # item['name']=item['name'].strip(' ').strip('\r').strip('\n').strip('\t').rstrip(' ').rstrip('\n').rstrip('\t').rstrip('\r')
        # item['title'] = "".join(item['name'].split())
        baseurls = urlparse(item['spider_link'])
        url_scheme = ""
        url_netloc = ""

        # spider_img
        if item['spider_img'] is not None:
            print(item['spider_img'])
            print("####")
            urls = urlparse(item['spider_img'])
            url_netloc = urls.netloc.strip()
            url_scheme = urls.scheme.strip()
            if not url_netloc:
                url_netloc = baseurls.netloc
            if not url_scheme:
                url_scheme = baseurls.scheme
            item['spider_img'] = url_scheme + "://" + url_netloc + urls.path

        # spider_imgs
        imgs = []
        if item['spider_imgs'] is not None:
            for img in item['spider_imgs']:
                parse_url = urlparse(img)
                url_netloc = parse_url.netloc.strip()
                url_scheme = parse_url.scheme.strip()
                if not url_netloc:
                    url_netloc = baseurls.netloc
                if not url_scheme:
                    url_scheme = baseurls.scheme
                imgs.append(url_scheme + "://" + url_netloc + parse_url.path)
        item['spider_imgs'] = imgs

        # content
        item['content'] = "".join(item['content'])

        return item
        # pass


class phpcmsSpiderPipeline(object):
    # cur=''
    def open_spider(self, spider):
        self.db = pymysql.connect(host='localhost', user='root', password='', db='phpcmsv9')
        self.cur = self.db.cursor()

        # self.file = open('../data/items.jl', 'w')

    def close_spider(self, spider):
        self.db.close()
        # self.file.close()

    def process_item(self, item, spider):
        insert_data = item
        sql = "insert into v9_collection_content (url,title,data) values (%s,%s,%s)"
        try:
            self.cur.execute(sql, (insert_data['url'], insert_data['title'], insert_data['data']))
            self.db.commit()
            pass
        except Exception as e:
            print(str(e))
            self.db.rollback()
        # finally:
        #     self.db.close()

        return item


class MysqlWriterPipeline(object):
    # cur=''
    def open_spider(self, spider):
        self.db = pymysql.connect(host='localhost', user='root', password='', db='phpcmsv9')
        self.cur = self.db.cursor()

        # self.file = open('../data/items.jl', 'w')

    def close_spider(self, spider):
        self.db.close()
        # self.file.close()

    def process_item(self, item, spider):
        insert_data = item

        if item['spider_img'] is None:
            insert_data['spider_img'] = ''
        if item['spider_imgs'] is None:
            insert_data['spider_imgs'] = ''

        if item['thumb'] is None:
            insert_data['thumb'] = ''
        if item['thumbs'] is None:
            insert_data['thumbs'] = ''

        if item['keywords'] is None:
            insert_data['keywords'] = ''
        if item['description'] is None:
            insert_data['description'] = ''

        sql = "insert into v9_news (catid,typeid,status,sysadd,spider_link,spider_img,spider_imgs,thumb,thumbs,title,keywords,description,inputtime,updatetime,create_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            # 值为空的item给删除了？
            self.cur.execute(sql, (
            insert_data['catid'], insert_data['typeid'], insert_data['status'], insert_data['sysadd'],
            insert_data['spider_link'], insert_data['spider_img'], insert_data['spider_imgs'], insert_data['thumb'],
            insert_data['thumbs'], insert_data['title'], '', '', insert_data['inputtime'], insert_data['updatetime'],
            insert_data['create_time']))
            self.cur.execute("select last_insert_id()")
            data = self.cur.fetchone()
            sql_data = "insert into v9_news_data(id,content) values (%s,%s)"
            self.cur.execute(sql_data, (data[0], insert_data['content']))
            self.db.commit()
            pass
        except Exception as e:
            print(str(e))
            self.db.rollback()
        # finally:
        #     self.db.close()

        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('../data/items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class MultiImagesPipeline(ImagesPipeline):
    # 从项目设置文件中导入图片下载路径
    img_store = get_project_settings().get('IMAGES_STORE')

    def get_media_requests(self, item, info):
        # for image_url in item['image_urls']:
        if item['spider_imgs']:
            for img in item['spider_imgs']:
                print(img + "$$$$$")
                yield scrapy.Request(img)

    def item_completed(self, results, item, info):
        image_path = [x['path'] for ok, x in results if ok]
        if not image_path:
            raise DropItem("Item contains no images")

        for img in image_path:
            pass
        # 定义分类保存的路径
        _path = image_path[0].lstrip("full/")
        _path1 = _path[0:2]
        _path2 = _path[2:4]
        img_path = "%s\\%s\\%s" % (self.img_store, _path1, _path2)
        # 目录不存在则创建目录
        if os.path.exists(img_path) == False:
            os.makedirs(img_path)
        # 将文件从默认下路路径移动到指定路径下
        shutil.move(self.img_store + image_path[0], img_path + "\\" + _path)

        item['thumb'] = _path1 + '/' + _path2 + '/' + _path
        print(item['thumb'])
        print(image_path)
        return item


class MyImagesPipeline(ImagesPipeline):
    # basepath="D:\xampp71\htdocs\phpcms\uploadfile"
    # 从项目设置文件中导入图片下载路径
    img_store = get_project_settings().get('IMAGES_STORE')

    def get_media_requests(self, item, info):
        # for image_url in item['image_urls']:
        if item['spider_imgs']:
            for img in item['spider_imgs']:
                yield scrapy.Request(img)

        if item['spider_img']:
            yield scrapy.Request(item['spider_img'])

    def item_completed(self, results, item, info):
        # for ok, x in results:
        #     if ok:
        #         print(x['path'])
        # result是一个包含tuple的容器
        # 容器中每个元素包含两个值，第一个代表状态True / False，第二个值是一个dict
        # 如果元素中状态为True则取dict中的path值
        # PEP0202列表递推式 https://www.python.org/dev/peps/pep-0202/
        item['thumbs'] = []
        image_res = [x for ok, x in results if ok]
        # 当程序出现错误，python会自动引发异常，也可以通过raise显示地引发异常。一旦执行了raise语句，raise后面的语句将不能执行。
        if not image_res:
            raise DropItem("Item contains no images")

        for img in image_res:
            image_path = img['path']
            image_url = img['url']
            # 定义分类保存的路径
            _path = image_path.lstrip("full/")
            _path1 = _path[0:2]
            _path2 = _path[2:4]

            # 目录不存在则创建目录
            img_target_path = "%s\\%s\\%s" % (self.img_store, _path1, _path2)
            if os.path.exists(img_target_path) == False:
                os.makedirs(img_target_path)

            # 将文件从默认下路路径移动到指定路径下
            img_target = img_target_path + "\\" + _path
            img_source = self.img_store + image_path
            if os.path.exists(img_source) == True:
                shutil.move(img_source, img_target)

            # 根据url判断是放到thumb 还是thumbs
            new_img_url = _path1 + '/' + _path2 + '/' + _path
            if item['spider_img'] == image_url:
                item['thumb'] = new_img_url
            if item['spider_imgs'].count(image_url) > 0:
                item['thumbs'].append(new_img_url)

        return item


'''
此示例演示如何从方法返回Deferredprocess_item()。
它使用Splash来呈现项目网址的屏幕截图。
Pipeline请求本地运行的Splash实例。
在请求被下载并且Deferred回调触发后，它将项目保存到一个文件并将文件名添加到项目。
'''


class ScreenshotPipeline(object):
    """Pipeline that uses Splash to render screenshot of
    every Scrapy item."""

    SPLASH_URL = "http://localhost:8050/render.png?url={}"

    def process_item(self, item, spider):
        encoded_item_url = quote(item["url"])
        screenshot_url = self.SPLASH_URL.format(encoded_item_url)
        request = scrapy.Request(screenshot_url)
        dfd = spider.crawler.engine.download(request, spider)
        dfd.addBoth(self.return_item, item)
        return dfd

    def return_item(self, response, item):
        if response.status != 200:
            # Error happened, return item.
            return item

        # Save screenshot to file, filename will be hash of url.
        url = item["url"]
        url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
        filename = "{}.png".format(url_hash)
        with open(filename, "wb") as f:
            f.write(response.body)

        # Store filename in item.
        item["screenshot_filename"] = filename
        return item
