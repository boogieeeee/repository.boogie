# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testtv100(ChannelTest, unittest.TestCase):
        index = "tv100:tv100:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class tv100(multi, scraper):
    title = u"TV 100"
    icon = "https://upload.wikimedia.org/wikipedia/tr/0/0f/TV100_logo.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "100"
    canlitvme_name = "TV100"
    youtube_chanid = "@tv100"
