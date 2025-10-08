# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testdmax(ChannelTest, unittest.TestCase):
        index = "dmax:dmax:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class dmax(multi, scraper):
    title = u"DMAX Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/DMAX_-_Logo_2016.svg/1200px-DMAX_-_Logo_2016.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "dmax"
    canlitv_ids = ["d-max-izle", "d-max-izle/2"]
    canlitvme_name = "D Max"
