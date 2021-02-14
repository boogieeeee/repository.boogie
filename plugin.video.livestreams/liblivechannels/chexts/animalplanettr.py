# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testanimalplanettr(ChannelTest, unittest.TestCase):
        index = "animalplanettr:animalplanet:"
        minepg = 0

except ImportError:
    pass


from liblivechannels import scraper
from scrapertools.multi import multi


class animalplanet(multi, scraper):
    title = u"Animal Planet Turkiye"
    icon = "https://i.pinimg.com/originals/ad/2e/57/ad2e57aa2d71eee1f79fb1b8fcb932da.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "animalplanet"
    ses_id = "animal-planet-izle"
