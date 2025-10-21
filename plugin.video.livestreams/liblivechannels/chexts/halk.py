# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testhalk(ChannelTest, unittest.TestCase):
        index = "halk:halk:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class halk(multi, scraper):
    title = u"Halk TV"
    icon = "https://upload.wikimedia.org/wikipedia/commons/4/42/Halk_TV_logo.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "Halk TV"
    youtube_chanid = "Halktvkanali"
    canlitvme_name = "halk tv"
    canlitv_id = "halk-tv"
