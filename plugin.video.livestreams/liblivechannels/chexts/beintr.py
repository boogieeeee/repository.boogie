# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testbein1(ChannelTest, unittest.TestCase):
        index = "beintr:bein1:"
        minlinks = 1

    class testbein2(ChannelTest, unittest.TestCase):
        index = "beintr:bein2:"
        minlinks = 1

    class testbein3(ChannelTest, unittest.TestCase):
        index = "beintr:bein3:"
        minlinks = 1

    class testbein4(ChannelTest, unittest.TestCase):
        index = "beintr:bein4:"
        minlinks = 1

    class testbeinmax1(ChannelTest, unittest.TestCase):
        index = "beintr:beinmax1:"
        minlinks = 1

    class testbeinmax2(ChannelTest, unittest.TestCase):
        index = "beintr:beinmax2:"
        minlinks = 1

    class testbeinhaber(ChannelTest, unittest.TestCase):
        index = "beintr:beinhaber:"
        minlinks = 1
except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class bein1(multi, scraper):
    title = u"Bein Sports 1 Turkiye"
    icon = "https://static.wikia.nocookie.net/logopedia/images/9/9d/BS1.svg/revision/latest/scale-to-width-down/512?cb=20200107203607"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "bein1"
    selcuk_name = "bein1"
    dady_name = "beinsports1turkey"
    acestreams = ["acestream://118416583faa3fb4f03800173429b6b844b43a52"]


class bein2(multi, scraper):
    title = u"Bein Sports 2 Turkiye"
    icon = "https://cdn-0.tvprofil.com/img/kanali-logo/bein_sports_2.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "bein2"
    selcuk_name = "bein2"
    dady_name = "beinsports2turkey"
    acestreams = ["acestream://48bee10b883f17c7186d60f1e8022dca0ba41a05"]


class bein3(multi, scraper):
    title = u"Bein Sports 3 Turkiye"
    icon = "https://cdn-0.tvprofil.com/img/kanali-logo/bein-sports-HD3.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "bein3"
    selcuk_name = "bein3"
    dady_name = "beinsports3turkey"
    acestreams = ["acestream://ed81c333815247536edfcdb2755147e8c4144d62"]


class bein4(multi, scraper):
    title = u"Bein Sports 4 Turkiye"
    icon = "https://static.wikia.nocookie.net/logopedia/images/b/bc/BS4.svg/revision/latest/scale-to-width-down/200?cb=20200107204039"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "bein4"
    selcuk_name = "bein4"
    dady_name = "beinsports4turkey"
    acestreams = ["acestream://7683cd0cbacf55fa8b39c363219ffba1bc47cf9d"]


class beinmax1(multi, scraper):
    title = u"Bein Sports Max 1 Turkiye"
    icon = "https://i.pinimg.com/originals/95/f6/68/95f6681b3ad0c0404b04a7c4a8cccb06.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "beinmax1"
    selcuk_name = "beinmax1"


class beinmax2(multi, scraper):
    title = u"Bein Sports Max 2 Turkiye"
    icon = "https://assets.bein.com/mena/sites/3/2015/06/beIN_SPORTS_MAX2_DIGITAL_Mono.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "beinmax2"
    selcuk_name = "beinmax2"


class beinhaber(multi, scraper):
    title = u"Bein Sports Haber"
    icon = "https://www.kolaytv.biz/bein-sports-haber.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "beinhaber"
    selcuk_name = "beinhaber"

