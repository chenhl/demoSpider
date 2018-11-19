# -*- coding: utf-8 -*-

class util(object):

    def genId(self,type,def_value=0):
        res = def_value
        if type == 'art':
            max = 999999
            res +=max
        return res