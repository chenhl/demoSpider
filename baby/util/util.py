# -*- coding: utf-8 -*-

class util:
    def genId(type, def_value=0):
        res = def_value
        if type == 'artist':
            max = 999999
            res += max
        return res
