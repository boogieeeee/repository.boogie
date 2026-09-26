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
    canlitvme_name = "atv"
    canlitvcenter_name = "atv"
    acestreams = ["acestream://5a92f2385120a631f0d9f08e5629a4d9c3be2e10"]


class ahaber(multi, scraper):
    title = u"A Haber"
    icon = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Ahaber_Logo.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_id = "a-haber"
    youtube_chanid = "@ahaber"
    canlitvcenter_name = "a haber"
    canlitvme_name = "A Haber"
    acestreams = ["acestream://8cbc6863e3072ab4fca0f26b076fdc046b3c683d"]
