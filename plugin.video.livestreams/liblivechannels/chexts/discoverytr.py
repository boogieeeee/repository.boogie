# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testdiscovery(ChannelTest, unittest.TestCase):
        index = "discoverytr:discoverychanneltr:"
        minlinks = 2

    class testdiscoveryscience(ChannelTest, unittest.TestCase):
        index = "discoverytr:discoverysciencetr:"
        minlinks = 2

except ImportError:
    pass


from liblivechannels import scraper
from scrapertools.multi import multi


class discoverychanneltr(multi, scraper):
    title = u"Discovery Channel Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/de/thumb/5/5f/Discovery_Channel_HD.svg/2000px-Discovery_Channel_HD.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "discovery"
    selcuk_name = "discovery"
    ses_ids = ["discovery-channel-izle"]


class discoverysciencetr(multi, scraper):
    title = u"Discovery Science Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Discovery_Science_2017_Logo.svg/1200px-Discovery_Science_2017_Logo.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "discoveryscience"
    selcuk_name = "discoveryscience"
    ses_ids = ["discovery-science-izle"]