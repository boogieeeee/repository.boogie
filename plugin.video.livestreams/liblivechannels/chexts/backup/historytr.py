# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testnatgeo(ChannelTest, unittest.TestCase):
        index = "historytr:hitory"
        minlinks = 2

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class history(multi, scraper):
    title = u"History Channel Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/History_Logo.svg/458px-History_Logo.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    selcuk_name = "history"
