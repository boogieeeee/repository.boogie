# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testbein1(ChannelTest, unittest.TestCase):
        index = "beintr:bein1:"
        minlinks = 2

    class testbein2(ChannelTest, unittest.TestCase):
        index = "beintr:bein2:"
        minlinks = 2

    class testbein3(ChannelTest, unittest.TestCase):
        index = "beintr:bein3:"
        minlinks = 2

    class testbein4(ChannelTest, unittest.TestCase):
        index = "beintr:bein4:"
        minlinks = 2

    class testbeinmax1(ChannelTest, unittest.TestCase):
        index = "beintr:beinmax1:"
        minlinks = 2

    class testbeinmax2(ChannelTest, unittest.TestCase):
        index = "beintr:beinmax2:"
        minlinks = 2

    class testbeinhaber(ChannelTest, unittest.TestCase):
        index = "beintr:beinhaber:"
        minlinks = 2
except ImportError:
    pass


from liblivechannels import scraper
from scrapertools.multi import multi


class bein1(multi, scraper):
    title = u"Bein Sports 1 Turkiye"
    icon = "https://static.wikia.nocookie.net/logopedia/images/9/9d/BS1.svg/revision/latest/scale-to-width-down/512?cb=20200107203607"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "bein1"
    selcuk_name = "bein1"
    ses_ids = ["beinsport-1-yedek-live", "beinsport-1-yedek1-live", "beinsport-1-yedek2-live"]


class bein2(multi, scraper):
    title = u"Bein Sports 2 Turkiye"
    icon = "https://d24j9r7lck9cin.cloudfront.net/l/o/6/6594.1491352241.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "bein2"
    selcuk_name = "bein2"
    ses_ids = ["beinsport-2-live", "beinsport-2-yedek-live"]


class bein3(multi, scraper):
    title = u"Bein Sports 3 Turkiye"
    icon = "https://d24j9r7lck9cin.cloudfront.net/l/o/6/6592.1491350506.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "bein3"
    selcuk_name = "bein3"
    ses_ids = ["beinsport-3-live"]


class bein4(multi, scraper):
    title = u"Bein Sports 4 Turkiye"
    icon = "https://static.wikia.nocookie.net/logopedia/images/b/bc/BS4.svg/revision/latest/scale-to-width-down/200?cb=20200107204039"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "bein4"
    selcuk_name = "bein4"
    ses_ids = ["beinsport-4-live"]


class beinmax1(multi, scraper):
    title = u"Bein Sports Max 1 Turkiye"
    icon = "https://i.pinimg.com/originals/95/f6/68/95f6681b3ad0c0404b04a7c4a8cccb06.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "beinmax1"
    selcuk_name = "beinmax1"
    ses_ids = ["beinsport-max1-live"]


class beinmax2(multi, scraper):
    title = u"Bein Sports Max 2 Turkiye"
    icon = "https://static.togglestatic.com/shain/v1/dataservice/ResizeImage/$value?Format=%27png%27&Quality=85&Width=640&Height=480&ImageUrl=1844650.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "beinmax2"
    selcuk_name = "beinmax2"
    ses_ids = ["beinsport-max2-live"]


class beinhaber(multi, scraper):
    title = u"Bein Sports Haber"
    icon = "https://www.kolaytv.biz/bein-sports-haber.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "beinhaber"
    selcuk_name = "beinhaber"
    ses_ids = ["beinsport-haber-live"]