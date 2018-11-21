# -*- coding: utf-8 -*-

class util:
    def genId(type, def_value=0):
        res = def_value
        if type == 'artist':
            #6 9
            max = 999999
            res += max
        elif type == 'exhibit':
            #7 9
            max = 9999999
            res += max
        return res

    def exhibitMeta(self) :
        meta = [{'txt': '展览名称：', 'code': 'name'},
                {'txt': '展览时间：', 'code': 'times'},
                {'txt': '开幕时间：', 'code': 'open_time'},
                {'txt': '展览机构：', 'code': 'org'},
                {'txt': '展览地址：', 'code': 'address'},
                {'txt': '展览备注：', 'code': 'msg'},
                {'txt': '展览城市：', 'code': 'area'},
                {'txt': '主办单位：', 'code': 'org_main'},
                {'txt': '承办单位：', 'code': 'org_manager'},
                {'txt': '协办单位：', 'code': 'org_slave'},
                {'txt': '参展艺术家：', 'code': 'artists'}]
        # meta2 = {'展览名称：':'name','展览时间：':'time','展览地点：':'area'}
        return meta