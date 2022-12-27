# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testnatgeowild(ChannelTest, unittest.TestCase):
        index = "natgeotr:natgeowild:"
        minlinks = 1

    class testnatgeo(ChannelTest, unittest.TestCase):
        index = "natgeotr:natgeo:"
        minlinks = 1

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class natgeowild(multi, scraper):
    title = u"NatGeo Wild Türkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Nat_Geo_Wild_logo.png/1200px-Nat_Geo_Wild_logo.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "natgeowild"
    selcuk_mobile = "36"
    selcuk_mobile_adaptive = False


class natgeo(multi, scraper):
    title = u"National Geographic Türkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/National-Geographic-Logo.svg/640px-National-Geographic-Logo.svg.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "nationalgeographic"
