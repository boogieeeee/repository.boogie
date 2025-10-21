# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testtele1(ChannelTest, unittest.TestCase):
        index = "tele1:tele1:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class tele1(multi, scraper):
    title = u"Tele 1"
    icon = "https://upload.wikimedia.org/wikipedia/tr/4/43/Tele1_logosu.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "Tele 1"
    canlitvme_name = "Tele1"
    youtube_chanid = "Tele1comtr"
