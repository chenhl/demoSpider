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
from urllib.parse import quote, urlparse, parse_qs, parse_qsl
import pymysql
# 导入项目设置
from scrapy.utils.project import get_project_settings
# 导入这个包为了移动文件
import shutil
# 这个包不解释
import os
import time
import pymongo
import re
from baby.util.util import util

from scrapy import selector


# 无用
class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['aid'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['aid'])
            return item


class baseItemPipeline(object):
    # 在你的多少范围内有展览 geo
    def process_item(self, item, spider):

        if 'title' not in item:
            raise DropItem('Item title is None')

        if 'spider_img' not in item:
            item['spider_img'] = ''
        if 'spider_imgs' not in item:
            item['spider_imgs'] = []
        if 'spider_imgs_text' not in item:
            item['spider_imgs_text'] = []

        if 'spider_tags' not in item:
            item['spider_tags'] = []
        if 'spider_userpic' not in item:
            item['spider_userpic'] = ''
        if 'spider_attr' not in item:
            item['spider_attr'] = {}
        if 'attr' not in item:
            item['attr'] = {}
        if 'spider_linkus' not in item:
            item['spider_linkus'] = {}
        if 'linkus' not in item:
            item['linkus'] = {}

        if 'tags' not in item:
            item['tags'] = []
        if 'thumb' not in item:
            item['thumb'] = ''
        if 'thumbs' not in item:
            item['thumbs'] = []
        if 'userpic' not in item:
            item['userpic'] = ''
        if 'uname' not in item:
            item['uname'] = ''

        if 'keywords' not in item:
            item['keywords'] = ''
        if 'description' not in item:
            item['description'] = ''

        if 'spider_content' not in item:
            item['spider_content'] = []
        if 'content' not in item:
            item['content'] = ''
        if 'spider_content2' not in item:
            item['spider_content2'] = []
        if 'content2' not in item:
            item['content2'] = ''
        # pics
        if 'content_pic' not in item:
            item['content_pic'] = []
        if 'spider_content_pic' not in item:
            item['spider_content_pic'] = []
        return item


class artsoArtistPipeline(object):
    def process_item(self, item, spider):
        # item['name']=item['name'].strip(' ').strip('\r').strip('\n').strip('\t').rstrip(' ').rstrip('\n').rstrip('\t').rstrip('\r')
        # item['title'] = "".join(item['name'].split())
        baseurls = urlparse(item['spider_link'])
        url_scheme = ""
        url_netloc = ""
        # spider_img
        if item['spider_img'] != '':
            urls = urlparse(item['spider_img'])
            url_netloc = urls.netloc.strip()
            url_scheme = urls.scheme.strip()
            if not url_netloc:
                url_netloc = baseurls.netloc
            if not url_scheme:
                url_scheme = baseurls.scheme
            item['spider_img'] = url_scheme + "://" + url_netloc + urls.path

        # tags
        # item['tags'] = item['spider_tags'].append(item['title'])
        tags = [item['title']]
        tags_str = ''
        if len(item['spider_tags']) > 0:
            for tag in item['spider_tags']:
                tags.append(tag)
        item['tags'] = tags

        # content
        item['content'] = "<p>" + "".join(item['spider_content']) + "</p>"
        return item


class galleryPipeline(object):
    def process_item(self, item, spider):
        # baseurls = urlparse(item['spider_link'])
        # img 过滤无图的item
        item['spider_img'] = item['spider_img'].strip(' ')
        if item['spider_img'] != '':
            if re.search('logo_default', item['spider_img']) is not None:
                # raise DropItem('Item img is default')
                item['spider_img'] = ''
                pass

        # attr 这儿可以不转换，etl时再转
        metas = util.galleryMeta(self)
        meta_attr = {}
        for meta in metas:
            meta_attr[meta['txt']] = meta['code']
        attr = {}
        if len(item['spider_attr']) > 0:
            for key in item['spider_attr']:
                if key not in meta_attr:
                    logging.info(key + 'not exists')
                else:
                    attr[meta_attr[key]] = item['spider_attr'][key]
            item['attr'] = attr

        # content
        if len(item['spider_content']) > 0:
            item['content'] = "<p>" + "".join(item['spider_content']) + "</p>"
        if len(item['spider_content2']) > 0:
            item['content2'] = "<p>" + "".join(item['spider_content2']) + "</p>"
        return item


class artsoExhibitPipeline(object):
    def process_item(self, item, spider):
        # attr 这儿可以不转换，etl时再转
        metas = util.exhibitMeta(self)
        meta_attr = {}
        for meta in metas:
            meta_attr[meta['txt']] = meta['code']
        # logging.info(metas)
        # logging.info(meta_attr)
        # logging.info(item['spider_attr'])
        attr = {}
        if len(item['spider_attr']) > 0:
            for key in item['spider_attr']:
                if key not in meta_attr:
                    logging.info(key + 'not exists')
                else:
                    attr[meta_attr[key]] = item['spider_attr'][key]
            item['attr'] = attr

        baseurls = urlparse(item['spider_link'])
        url_scheme = ""
        url_netloc = ""
        # spider_imgs 和 text一一对应
        imgs = []
        if len(item['spider_imgs_text']) > 0:
            for img in item['spider_imgs_text']:
                if re.search('/off.jpg', img['img']) is None:
                    imgs.append(img['img'])

        item['spider_imgs'] = imgs
        if len(imgs) > 0:
            item['spider_img'] = imgs[0]

        # content
        if len(item['spider_content']) > 0:
            item['content'] = "<p>" + "".join(item['spider_content']) + "</p>"

        return item


class newsSohuPipeline(object):
    def process_item(self, item, spider):
        baseurls = urlparse(item['spider_link'])
        url_scheme = ""
        url_netloc = ""
        # spider_img
        if item['spider_img'] != '':
            urls = urlparse(item['spider_img'])
            url_netloc = urls.netloc.strip()
            url_scheme = urls.scheme.strip()
            if not url_netloc:
                url_netloc = baseurls.netloc
            if not url_scheme:
                url_scheme = baseurls.scheme
            item['spider_img'] = url_scheme + "://" + url_netloc + urls.path

        # spider_userpic
        if item['spider_userpic'] != '':
            urls = urlparse(item['spider_userpic'])
            url_netloc = urls.netloc.strip()
            url_scheme = urls.scheme.strip()
            if not url_netloc:
                url_netloc = baseurls.netloc
            if not url_scheme:
                url_scheme = baseurls.scheme
            item['spider_userpic'] = url_scheme + "://" + url_netloc + urls.path

        # spider_imgs
        imgs = []
        if len(item['spider_imgs']) > 0:
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

        # content_pic
        if len(item['content_pic']) > 0:
            for i in range(len(item['content_pic'])):
                parse_url = urlparse(item['content_pic'][i]['img'])
                url_netloc = parse_url.netloc.strip()
                url_scheme = parse_url.scheme.strip()
                if not url_netloc:
                    url_netloc = baseurls.netloc
                if not url_scheme:
                    url_scheme = baseurls.scheme
                item['content_pic'][i]['img'] = url_scheme + "://" + url_netloc + parse_url.path

        # spider_tags
        tags = []
        tags_str = ''
        if len(item['spider_tags']) > 0:
            for tag in item['spider_tags']:
                if tag['name'] is not None:
                    tags.append(tag['name'])
        item['tags'] = tags
        # content
        del item['content'][0:2]
        # del item['content'][-3:]
        # item['content'] = "".join(item['content'])
        if len(item['content']) > 0:
            for i in range(len(item['content'])):
                if re.search('点击进入搜狐首页', item['content'][i]) is not None or re.search('返回搜狐',
                                                                                      item['content'][i]) is not None:
                    item['content'][i] = ''  # 直接del有错误 for的长度未变

        item['content'] = "".join(item['content'])
        return item


# 文章内容图片处理
class contentImagesPipeline(object):
    def process_item(self, item, spider):
        pass


class MysqlDB(object):
    def open_spider(self, spider):
        env = os.environ
        try:
            self.db = pymysql.connect(host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']), user=env['MYSQL_USERNAME'],
                                      password=env['MYSQL_PASSWORD'], db=env['MYSQL_DATABASE'])
        except Exception as e:
            # 关闭spider
            print(e)
            logging.info(e)
            spider.crawler.engine.close_spider('mysql connect error')
            pass

        self.cur = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def update_member(self, items):
        # insert_data = items
        sql = "select userid from v9_member where uid = %s"
        try:
            self.cur.execute(sql, (items['uid']))
            self.db.commit()
            _data = self.cur.fetchone()
            if _data is not None:
                try:
                    sql_update = "update v9_member set publish_num = publish_num+1 where userid = %s"
                    self.cur.execute(sql_update, (_data[0]))
                    self.db.commit()
                    # logging.info('')
                except Exception as e0:
                    print(str(e0))
                    logging.info('update ' + items['uname'] + ' error')
                    self.db.rollback()
            else:
                try:
                    sql_insert = "insert into v9_member (uid,username,nickname,userpic,groupid,publish_num,create_time) values (%s,%s,%s,%s,%s,%s,%s)"
                    self.cur.execute(sql_insert, (
                        items['uid'],
                        items['uname'],
                        items['uname'],
                        items['userpic'],
                        '9',
                        '1',
                        items['create_time']
                    ))
                    self.cur.execute("select last_insert_id()")

                    data = self.cur.fetchone()
                    sql_insert = "insert into v9_member_detail (userid) values (%s)"
                    self.cur.execute(sql_insert, (
                        data[0]
                    ))
                    self.db.commit()
                    logging.info('insert ' + items['uname'])
                except Exception as e1:
                    print(str(e1))
                    logging.info(e1)
                    logging.info('insert ' + items['uname']+' error')
                    self.db.rollback()
        except Exception as e:
            print(str(e))
            logging.info(e)
            logging.info(str(e))
            self.db.rollback()
            scrapy.exceptions.CloseSpider('mysql update error')

    def insert_db(self, items):
        insert_data = items
        insert_data['spider_imgs'] = json.dumps(insert_data['spider_imgs'])
        insert_data['spider_imgs_text'] = json.dumps(insert_data['spider_imgs_text'])
        insert_data['thumbs'] = json.dumps(insert_data['thumbs'])
        insert_data['spider_tags'] = json.dumps(insert_data['spider_tags'])
        insert_data['tags'] = json.dumps(insert_data['tags'])

        insert_data['attr'] = json.dumps(insert_data['attr'])
        insert_data['linkus'] = json.dumps(insert_data['linkus'])
        insert_data['spider_attr'] = json.dumps(insert_data['spider_attr'])
        insert_data['spider_linkus'] = json.dumps(insert_data['spider_linkus'])
        if len(insert_data['content_pic']) > 0:
            insert_data['content_pic'] = json.dumps(insert_data['content_pic'])
        else:
            insert_data['content_pic'] = ''

        if len(insert_data['spider_content_pic']) > 0:
            insert_data['spider_content_pic'] = json.dumps(insert_data['spider_content_pic'])
        else:
            insert_data['spider_content_pic'] = ''

        sql = "insert into v9_news (aid,catid,typeid,status,sysadd,uid,uname,userpic,attr,linkus,spider_attr,spider_linkus,spider_name,spider_tags,tags,spider_link,spider_img,spider_userpic,spider_imgs,spider_imgs_text,thumb,thumbs,title,keywords,description,inputtime,updatetime,create_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            eret = self.cur.execute(sql, (
                insert_data['aid'],
                insert_data['catid'],
                insert_data['typeid'],
                insert_data['status'],
                insert_data['sysadd'],
                insert_data['uid'],
                insert_data['uname'],
                insert_data['userpic'],
                insert_data['attr'],
                insert_data['linkus'],
                insert_data['spider_attr'],
                insert_data['spider_linkus'],
                insert_data['spider_name'],
                insert_data['spider_tags'],
                insert_data['tags'],
                insert_data['spider_link'],
                insert_data['spider_img'],
                insert_data['spider_userpic'],
                insert_data['spider_imgs'],
                insert_data['spider_imgs_text'],
                insert_data['thumb'],
                insert_data['thumbs'],
                insert_data['title'],
                insert_data['keywords'],
                insert_data['description'],
                insert_data['inputtime'],
                insert_data['updatetime'],
                insert_data['create_time']))
            self.cur.execute("select last_insert_id()")
            data = self.cur.fetchone()
            sql_data = "insert into v9_news_data(id,content,content2,pictureurls,spider_content_pic) values (%s,%s,%s,%s,%s)"
            self.cur.execute(sql_data, (
                data[0], insert_data['content'], insert_data['content2'], insert_data['content_pic'],
                insert_data['spider_content_pic']))
            self.db.commit()
            return True
        except Exception as e:
            print(str(e))
            logging.info(items['spider_link'] + ' ' + items['title'])
            self.db.rollback()
            scrapy.exceptions.CloseSpider('mysql insert error')
            return False

    def update_db(self, items):
        insert_data = items
        insert_data['tags'] = json.dumps(insert_data['tags'])
        sql = "update v9_news set tags = %s where id = %s"
        logging.info(sql + 'tags:' + items['tags'] + ',id=' + str(insert_data['auto_id']))
        try:
            self.cur.execute(sql, (insert_data['tags'], insert_data['auto_id']))
            self.db.commit()
            return True
        except Exception as e:
            print(str(e))
            logging.info(str(e))
            self.db.rollback()
            scrapy.exceptions.CloseSpider('mysql update error')
            return False

    def select_db(self, items):
        insert_data = items
        sql = "select id from v9_news where spider_link = %s"
        try:
            self.cur.execute(sql, (insert_data['spider_link']))
            self.db.commit()
            _data = self.cur.fetchone()
            if _data is not None:
                return True
            else:
                return False

        except Exception as e:
            print(str(e))
            self.db.rollback()
            scrapy.exceptions.CloseSpider('mysql select error')
            return False


# item是否抓取过
class itemExistsPipeline(MysqlDB):
    def process_item(self, item, spider):
        res = self.select_db(item)
        if res:
            raise DropItem("Item " + item['spider_link'] + " exists")
        else:
            return item

# 更新发布者信息 insert or update member表
# 只根据uid判断重复，所以只适合于一个站（newsSohu）
class MysqlMemberPipeline(MysqlDB):
    def process_item(self, item, spider):
        self.update_member(item)
        return item

# 直接insert
class MysqlWriterPipeline(MysqlDB):
    def process_item(self, item, spider):
        self.insert_db(item)
        return item


# insert 或 update
class MysqlUpdatePipeline(MysqlDB):
    # self.file.close()
    def process_item(self, item, spider):
        insert_data = item
        # 查询名称是否存在
        sel_sql = "select id,aid,title,tags from v9_news where title = %s"
        # print(sel_sql+' s='+insert_data['title'])
        logging.info(sel_sql + ' s=' + insert_data['title'])
        try:
            self.cur.execute(sel_sql, (insert_data['title']))
            self.db.commit()
            _data = self.cur.fetchone()
            if _data is not None:
                data_tags = json.loads(_data[3])
                # logging.info(data_tags)
                item_tags = insert_data['spider_tags'][0]
                # logging.info(item_tags)
                # print(data_tags)
                # print(item_tags)
                # print(insert_data['tags'])
                # print('----------')
                if item_tags not in data_tags:
                    data_tags.append(item_tags)
                    insert_data['tags'] = data_tags
                    insert_data['auto_id'] = _data[0]
                    self.update_db(insert_data)
            else:
                print(insert_data['title'])
                logging.info('insert:' + insert_data['title'])
                self.insert_db(insert_data)
        except Exception as e:
            scrapy.exceptions.CloseSpider('mysql select error2')
            pass

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
        if len(item['spider_imgs']) > 0:
            for img in item['spider_imgs']:
                yield scrapy.Request(img)

        if len(item['content_pic']) > 0:
            for img in item['content_pic']:
                yield scrapy.Request(img['img'])

        if item['spider_img'] != '':
            yield scrapy.Request(item['spider_img'])

        if item['spider_userpic'] != '':
            yield scrapy.Request(item['spider_userpic'])

        return None

    # resulsts是当前item的所有图片下载结果
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
        # if not image_res:
        #     raise DropItem("Item contains no images")
        #
        if len(image_res) > 0:
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
                    # item['thumb_src']=image_res
                if item['spider_userpic'] == image_url:
                    item['userpic'] = new_img_url
                    # item['userpic_src'] = image_res
                if item['spider_imgs'].count(image_url) > 0 and item['thumbs'].count(new_img_url) == 0:
                    item['thumbs'].append(new_img_url)

                if len(item['content_pic']) > 0:
                    for i in range(len(item['content_pic'])):
                        if item['content_pic'][i]['img'] == image_url:
                            item['content_pic'][i]['img'] = new_img_url

                    # item['thumbs_src'].append(image_res)

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
