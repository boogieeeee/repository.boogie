# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testdmax(ChannelTest, unittest.TestCase):
        index = "discovery:dmax:"

    class testdiscovery(ChannelTest, unittest.TestCase):
        index = "discovery:discovery:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class dmax(multi, scraper):
    title = u"DMAX Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/DMAX_-_Logo_2016.svg/1200px-DMAX_-_Logo_2016.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "dmax"
    canlitvcenter_name = "dmax"
    canlitvme_name = "D Max"

    def get(self):
        for link in super().get():
            if "dogus" not in link.url:
                yield link


class discovery(multi, scraper):
    title = u"Discovery Channel Turkiye"
    icon = "https://reelcreativevideos.com/wp-content/uploads/2015/10/discovery-channel-logo.png?w=400"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "discovery channel"
    acestreams = ["acestream://1534834fc65764c8eaca43cf108e0b49158d8c68"]
