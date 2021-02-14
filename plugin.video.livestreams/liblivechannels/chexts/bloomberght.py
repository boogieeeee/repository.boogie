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
from scrapertools.multi import multi


class bloomberght(multi, scraper):
    title = u"Bloomberg HT"
    icon = "http://www.bloomberght.com/images/logo.png"
    youtube_chanid = "bloomberght"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "bloomberght"
