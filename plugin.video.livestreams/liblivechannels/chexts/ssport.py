# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testssport1(ChannelTest, unittest.TestCase):
        index = "ssport:ssport1:"
        minlinks = 2

    class testssport2(ChannelTest, unittest.TestCase):
        index = "ssport:ssport2:"
        minlinks = 2
        minepg = 0

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class ssport1(multi, scraper):
    title = u"S Sport 1"
    icon = "https://upload.wikimedia.org/wikipedia/tr/thumb/8/82/S_Sport_logo.jpg/800px-S_Sport_logo.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "ssport"
    selcuk_name = "ssport"
    ses_ids = ["ssport-live"]


class ssport2(multi, scraper):
    title = u"S Sport 2"
    icon = "https://upload.wikimedia.org/wikipedia/tr/thumb/e/ed/S_Sport_2_logo.jpg/800px-S_Sport_2_logo.png"
    categories = [u"Türkçe", u"Spor"]
    selcuk_name = "ssport2"
    ses_ids = ["ssport2-live"]
