# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testbbcearth(ChannelTest, unittest.TestCase):
        index = "bbc:earth:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class earth(multi, scraper):
    title = u"BBC Earth Turkiye"
    icon = "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3f/BBC_Earth.svg/330px-BBC_Earth.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    acestreams = ["acestream://95e8ae652b5f5fa653be611aaac2f736dcf67ba2"]
