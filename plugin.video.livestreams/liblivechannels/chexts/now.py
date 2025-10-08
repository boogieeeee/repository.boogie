# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testnow(ChannelTest, unittest.TestCase):
        index = "now:now:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class now(multi, scraper):
    title = u"NOW"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/NOW_TV_%28Turkey%29_wordmark-red.svg/640px-NOW_TV_%28Turkey%29_wordmark-red.svg.png"
    categories = [u"Türkçe", u"Realiti"]
    yayin_name = "now"
    youtube_chanid = "nowtvturkiye"
    canlitvme_name = "now"
    canlitv_id = "now-tv"
