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
