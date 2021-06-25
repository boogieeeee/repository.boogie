# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testshowtv(ChannelTest, unittest.TestCase):
        index = "showtv:showtv:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class showtv(multi, scraper):
    title = u"Show TV"
    icon = "http://www.freelogovectors.net/wp-content/uploads/2018/04/show_tv_logo_freelogovectors.net_.png"
    youtube_chanid = "ShowTV"
    categories = [u"Türkçe", u"Realiti"]
    yayin_name = "show"
