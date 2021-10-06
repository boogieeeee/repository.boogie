# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testespn(ChannelTest, unittest.TestCase):
        index = "espn:espn:"
        minepg = 0

    class testespn2(ChannelTest, unittest.TestCase):
        index = "espn:espn2:"
        minepg = 0

except ImportError:
    pass


from liblivechannels.chexts.scrapertools.multi import multi
from liblivechannels import scraper


class espn(multi, scraper):
    icon = "https://logosmarken.com/wp-content/uploads/2020/12/ESPN-Logo-650x366.png"
    title = "ESPN"
    sports24_id = "espn"
    dady_name = "espnusa"
    vercel_id = "10179"


class espn2(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/ESPN2_logo.svg/800px-ESPN2_logo.svg.png"
    title = "ESPN 2"
    sports24_id = "espn2"
    dady_name = "espn2usa"
    vercel_id = "12444"
