
# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testtv8(ChannelTest, unittest.TestCase):
        index = "tv8:tv8:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi
from tinyxbmc import net, mediaurl
import re


class tv8(multi, scraper):
    title = u"TV 8"
    icon = "https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Tv8_new_logo.png/125px-Tv8_new_logo.png"
    categories = [u"Türkçe", u"Realiti"]
    yayin_id = "tv-8"
    selcuk_name = "8"
    kolay_ids = ["/tv8-canli-yayinlar", "/tv8-canli-yayinlar/2", "/tv8-canli-yayinlar/3", "/tv8-canli-yayinlar/4"]
    canlitv_ids = ["tv-8-canli-hd", "tv-8-canli-hd/2"]

    def get(self):
        for stream in multi.get(self):
            yield stream
        tv8url = "https://www.tv8.com.tr/canli-yayin"
        page = net.http(tv8url)
        yield mediaurl.hlsurl(re.findall("file\s?:\s?(?:\"|\')(https:\/\/.+?)(?:\"|\')", page)[0],
                         headers={"Referer": tv8url})
