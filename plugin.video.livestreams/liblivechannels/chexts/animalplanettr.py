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
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Animal_Planet_logo.svg/1200px-Animal_Planet_logo.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "animalplanet"
    ses_id = "animal-planet-izle"
