# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testlofi1(ChannelTest, unittest.TestCase):
        index = "lofi:lofi1:"
        minepg = 0

    class testlofi2(ChannelTest, unittest.TestCase):
        index = "lofi:lofi2:"
        minepg = 0

except ImportError:
    pass


from liblivechannels import scraper
from scrapertools.multi import multi


class lofi1(multi, scraper):
    title = u"LO-FI Channel 1"
    icon = "https://www.tubefilter.com/wp-content/uploads/2020/02/chilledcow-youtube-terminated-1024x629.jpg"
    youtube_chanid = "ChilledCow"
    categories = [u"Music"]


class lofi2(multi, scraper):
    title = u"LO-FI Channel 2"
    icon = "https://i.ytimg.com/vi/zFhfksjf_mY/maxresdefault.jpg"
    youtube_chanid = "ChilledCow"
    youtube_sindex = 1
    categories = [u"Music"]
