# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testtv8(ChannelTest, unittest.TestCase):
        index = "tv8:tv8:"
except ImportError:
    pass


from liblivechannels import scraper
from scrapertools.multi import multi


class tv8(multi, scraper):
    title = u"TV 8"
    icon = "https://img.tv8.com.tr/s/template/v2/img/tv8-logo.png"
    categories = [u"Türkçe", u"Realiti"]
    yayin_id = "tv-8"
    selcuk_name = "8"
    ses_id = "tv8-izle"
    kolay_id = "/tv8-canli-hd"

    def get(self):
        yield "https://tv8.personamedia.tv/tv8hls?fmt=hls"
        for stream in multi.get(self):
            yield stream
