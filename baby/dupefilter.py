# -*- coding: utf-8 -*-

from scrapy.dupefilters import RFPDupeFilter
from urllib.parse import urlparse
class itemDupeFilter(RFPDupeFilter):
    def __init__(self):
        self.v_url = set()

    def request_seen(self, request):
        url = request.url
        urls = urlparse(url)

        pass
