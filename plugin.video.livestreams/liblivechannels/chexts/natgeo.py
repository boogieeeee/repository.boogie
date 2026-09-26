# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testnatgeo(ChannelTest, unittest.TestCase):
        index = "natgeo:natgeo:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class natgeo(multi, scraper):
    title = u"Nat Geo Wild Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/f/f1/NGWild.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "national geographic wild"
    acestreams = ["acestream://cd966b57027f521c8d78251519b7cd8edc15f68a"]
