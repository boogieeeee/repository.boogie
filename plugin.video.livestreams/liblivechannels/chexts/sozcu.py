# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testsozcu(ChannelTest, unittest.TestCase):
        index = "sozcu:sozcu:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class sozcu(multi, scraper):
    title = u"Sözcü TV"
    icon = "https://upload.wikimedia.org/wikipedia/tr/e/ed/SZC_TV_logo.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "Sözcü TV"
    youtube_chanid = "Sozcutelevizyonu"
    youtube_sindex = -1
    canlitvme_name = "sozcu"
