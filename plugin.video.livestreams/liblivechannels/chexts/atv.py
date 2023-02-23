'''
Created on Jun 11, 2022

@author: boogie
'''
# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testatv(ChannelTest, unittest.TestCase):
        index = "atv:atv:"

    class testahaber(ChannelTest, unittest.TestCase):
        index = "atv:ahaber:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class atv(multi, scraper):
    title = u"atv"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Atv_logo_2010.svg/1280px-Atv_logo_2010.svg.png"
    categories = [u"Türkçe", u"Realiti"]
    yayin_id = "atv"
    youtube_chanid = "ATVTurkiye"
    kolay_ids = ["/atv-canli-donmadan/1", "/atv-canli-donmadan/2", "/atv-canli-donmadan/3"]


class ahaber(multi, scraper):
    title = u"A Haber"
    icon = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Ahaber_Logo.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_id = "a-haber"
    youtube_chanid = "ahaber"
    kolay_ids = ["/a-haber/1", "/a-haber/2", "/a-haber/3", "/a-haber/4"]
    canlitv_ids = ["a-haber-izle/1", "a-haber-izle/2"]
