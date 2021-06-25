# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testntv(ChannelTest, unittest.TestCase):
        index = "ntv:ntv:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class ntv(multi, scraper):
    title = u"NTV"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/NTV_logo.png/800px-NTV_logo.png"
    youtube_chanid = "NTV"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "n"
