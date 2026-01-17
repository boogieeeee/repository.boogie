# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testbloomberght(ChannelTest, unittest.TestCase):
        index = "bloomberght:bloomberght:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class bloomberght(multi, scraper):
    title = u"Bloomberg HT"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Bloomberg_HT_logo.svg/640px-Bloomberg_HT_logo.svg.png"
    youtube_chanid = "@bloomberght"
    categories = [u"Türkçe", u"Haber"]
    canlitvme_name = "Bloomberg HT"
    yayin_name = "bloomberght"
