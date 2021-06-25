# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testnatgeo(ChannelTest, unittest.TestCase):
        index = "natgeotr:natgeowild:"
        minlinks = 2

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class natgeowild(multi, scraper):
    title = u"NatGeo Wild Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Nat_Geo_Wild_logo.png/1200px-Nat_Geo_Wild_logo.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "natgeowild"
    selcuk_name = "natgeowild"
    ses_ids = ["national-geo-wild-izle"]
