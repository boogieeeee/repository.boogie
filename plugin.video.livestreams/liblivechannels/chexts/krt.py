# -*- encoding: utf-8 -*-
'''
Created on Feb 13, 2021

@author: boogie
'''
try:
    import unittest
    from test import ChannelTest

    class testkrt(ChannelTest, unittest.TestCase):
        index = "krt:krt:"
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class krt(multi, scraper):
    title = u"KRT"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/KRT_Logo_2023.webp/500px-KRT_Logo_2023.webp.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "KRT"
    canlitvme_name = "krt tv"
    youtube_chanid = "@krtcanli"
