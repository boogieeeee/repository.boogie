# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testhistory(ChannelTest, unittest.TestCase):
        index = "historytr:historytr:"
        minepg = 0
        minlinks = 1

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class historytr(multi, scraper):
    title = u"History Channel Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/History_Logo.svg/458px-History_Logo.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    # selcuk_mobile = "40"
    # selcuk_mobile_adaptive = False
