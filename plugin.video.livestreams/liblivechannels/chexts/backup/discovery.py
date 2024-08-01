# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testdiscovery(ChannelTest, unittest.TestCase):
        index = "discovery:discoverychanneltr:"
        minlinks = 0

    class testdiscoveryscience(ChannelTest, unittest.TestCase):
        index = "discovery:discoverysciencetr:"
        minlinks = 0

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class discoverychanneltr(multi, scraper):
    title = u"Discovery Channel Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/de/thumb/5/5f/Discovery_Channel_HD.svg/2000px-Discovery_Channel_HD.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "discovery"


class discoverysciencetr(multi, scraper):
    title = u"Discovery Science Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Discovery_Science_2017_Logo.svg/1200px-Discovery_Science_2017_Logo.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "discoveryscience"
