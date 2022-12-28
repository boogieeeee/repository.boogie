# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testskyf1de(ChannelTest, unittest.TestCase):
        index = "sky:skyf1de:"
        minlinks = 1

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class skyf1de(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Sky_Sport_F1_-_Logo_2020.svg/512px-Sky_Sport_F1_-_Logo_2020.svg.png"
    title = "Sky Sport F1 Deutschland"
    acestreams = ["acestream://b04372b9543d763bd2dbd2a1842d9723fd080076"]
