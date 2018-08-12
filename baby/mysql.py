# -*- coding: utf-8 -*-

import pymysql

# 打开数据库连接
db = pymysql.connect(host="localhost", user="root",
                     password="", db="yishujia", port=3306)

# 使用cursor()方法获取操作游标
cur = db.cursor()
sql_insert = """insert into a_artist(name,content) values('liu','')"""

try:
    cur.execute(sql_insert)
    # 提交
    db.commit()
except Exception as e:
    # 错误回滚
    db.rollback()
finally:
    db.close()