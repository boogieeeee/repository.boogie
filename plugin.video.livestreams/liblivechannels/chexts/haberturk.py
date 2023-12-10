# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testhaberturk(ChannelTest, unittest.TestCase):
        index = "haberturk:haberturk:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class haberturk(multi, scraper):
    title = u"Haber Türk"
    icon = "https://lh3.googleusercontent.com/RHV4WLdQNalCG87rSH5Q60ZDEnHMg1_Az679Dg6DglSinOxdyD3W80VLpn7SlSjd1Q=w300"
    youtube_chanid = "haberturktv"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "haberturk"
    canlitvme_name = "Habertürk Tv"
