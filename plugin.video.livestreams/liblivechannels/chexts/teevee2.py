# -*- encoding: utf-8 -*-
'''
Created on Jun 6, 2021

@author: boogie
'''

try:
    import unittest
    from test import ChannelTest

    class testdmax(ChannelTest, unittest.TestCase):
        index = "teevee2:teevee2:"

except ImportError:
    pass


from liblivechannels import scraper
from scrapertools.multi import multi


class teevee2(multi, scraper):
    title = u"Teve 2"
    icon = "https://upload.wikimedia.org/wikipedia/en/c/ca/Teve2_logo.png"
    categories = [u"Türkçe", u"Realiti"]
    kolay_id = "/teve2"
    yayin_name = "teve2"
    sesid = "teve2-izle"
