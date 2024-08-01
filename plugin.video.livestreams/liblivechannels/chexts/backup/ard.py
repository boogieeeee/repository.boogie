# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testdasesrte(ChannelTest, unittest.TestCase):
        index = "ard:daserste:"
        minepg = 0

    class testbrsud(ChannelTest, unittest.TestCase):
        index = "ard:brsud:"
        minepg = 0

    class testhr(ChannelTest, unittest.TestCase):
        index = "ard:hr:"
        minepg = 0

    class testmdr(ChannelTest, unittest.TestCase):
        index = "ard:mdr:"
        minepg = 0

    class testndr(ChannelTest, unittest.TestCase):
        index = "ard:ndr:"
        minepg = 0

    class testrbb(ChannelTest, unittest.TestCase):
        index = "ard:rundfunkberlin:"
        minepg = 0

    class testsr(ChannelTest, unittest.TestCase):
        index = "ard:saarrundfunk:"
        minepg = 0

    class testswr(ChannelTest, unittest.TestCase):
        index = "ard:swr:"
        minepg = 0

    class testwr(ChannelTest, unittest.TestCase):
        index = "ard:westrundfunk:"
        minepg = 0

    class testone(ChannelTest, unittest.TestCase):
        index = "ard:one:"
        minepg = 0

    class testardalpha(ChannelTest, unittest.TestCase):
        index = "ard:ardalpha:"
        minepg = 0

    class testarte(ChannelTest, unittest.TestCase):
        index = "ard:arte:"
        minepg = 0

    class test3dat(ChannelTest, unittest.TestCase):
        index = "ard:dreisat:"
        minepg = 0

    class testkika(ChannelTest, unittest.TestCase):
        index = "ard:kika:"
        minepg = 0

    class testphoenix(ChannelTest, unittest.TestCase):
        index = "ard:phoenix:"
        minepg = 0

    class testts(ChannelTest, unittest.TestCase):
        index = "ard:tagesschau:"
        minepg = 0

    class testdw(ChannelTest, unittest.TestCase):
        index = "ard:dw:"
        minepg = 0

except ImportError:
    pass


from liblivechannels.chexts.scrapertools.mediathek import multi
from liblivechannels import scraper


class daserste(multi, scraper):
    sender = "Das Erste"
    icon = multi.iconpath + "tv-das-erste.png"
    title = sender


class brsud(multi, scraper):
    sender = u"BR Fernsehen - Süd"
    icon = multi.iconpath + "tv-br.png"
    title = sender


class hr(multi, scraper):
    sender = u"hr-fernsehen"
    icon = multi.iconpath + "tv-hr.png"
    title = "HR Fernsehen"


class mdr(multi, scraper):
    sender = u"MDR Sachsen"
    icon = multi.iconpath + "tv-mdr-sachsen.png"
    title = sender


class ndr(multi, scraper):
    sender = u"NDR Fernsehen"
    icon = multi.iconpath + "tv-ndr-niedersachsen.png"
    title = sender


class rundfunkberlin(multi, scraper):
    sender = u"Rundfunk Berlin Brandenburg"
    icon = multi.iconpath + "tv-rbb-berlin.png"
    title = sender


class saarrundfunk(multi, scraper):
    sender = u"Saarländischer Rundfunk"
    icon = multi.iconpath + "tv-sr.png"
    title = sender


class swr(multi, scraper):
    sender = u"SWR Baden-Württemberg"
    icon = multi.iconpath + "tv-swr.png"
    title = sender


class westrundfunk(multi, scraper):
    sender = u"Westdeutscher Rundfunk"
    icon = multi.iconpath + "tv-wdr.png"
    title = sender


class one(multi, scraper):
    sender = u"ONE"
    icon = multi.iconpath + "tv-one.png"
    title = sender


class ardalpha(multi, scraper):
    sender = u"ARD-alpha"
    icon = multi.iconpath + "tv-alpha.png"
    title = sender


class arte(multi, scraper):
    sender = u"arte"
    icon = multi.iconpath + "tv-arte.png"
    title = sender


class dreisat(multi, scraper):
    sender = u"3sat"
    icon = multi.iconpath + "tv-3sat.png"
    title = sender


class kika(multi, scraper):
    sender = u"KiKA"
    icon = multi.iconpath + "tv-kika.png"
    title = sender


class phoenix(multi, scraper):
    sender = u"Phoenix"
    icon = multi.iconpath + "tv-phoenix.png"
    title = sender


class tagesschau(multi, scraper):
    sender = u"tagesschau24"
    icon = multi.iconpath + "tv-tagesschau24.png"
    title = sender


class dw(multi, scraper):
    sender = u"Deutsche Welle"
    icon = multi.iconpath + "tv-deutsche-welle.png"
    title = sender
