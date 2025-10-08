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
    icon = "https://tr.wikipedia.org/wiki/S%C3%B6zc%C3%BC_TV#/media/Dosya:SZC_TV_logo.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "Sözcü TV"
    youtube_chanid = "Sozcutelevizyonu"
    canlitvme_name = "sozcu"
