# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testcnnturk(ChannelTest, unittest.TestCase):
        index = "cnnturk:cnnturk:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class cnnturk(multi, scraper):
    title = u"CNN Türk"
    icon = "http://www.gundemgazetesi.net/d/other/cnn_t_rk-001.png"
    youtube_chanid = "@cnnturk"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "cnnturk"
    canlitvme_name = "CNN Türk"
    canlitvcenter_name = "CNN Türk"
    acestreams = ["acestream://dbbf25af5c60d5b5926cfd457de4336c3307efc5"]
