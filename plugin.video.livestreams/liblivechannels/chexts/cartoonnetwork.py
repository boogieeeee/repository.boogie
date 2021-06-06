# -*- encoding: utf-8 -*-
'''
Created on Jun 6, 2021

@author: boogie
'''

try:
    import unittest
    from test import ChannelTest

    class testdmax(ChannelTest, unittest.TestCase):
        index = "cartoonnetwork:cntr:"

except ImportError:
    pass


from liblivechannels import scraper
from scrapertools.multi import multi


class cntr(multi, scraper):
    title = u"Cartoon Network Turkiye"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Cartoon_Network_2010_logo.svg/200px-Cartoon_Network_2010_logo.svg.png"
    categories = [u"Türkçe", u"Realiti"]
    kolay_id = "/cartoon-network"
    yayin_name = "cartoon-network"
    sesid = "cortoon-network-izle"
