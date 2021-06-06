# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testtrt1(ChannelTest, unittest.TestCase):
        index = "trt1:trt1:"

    class testtrtspor(ChannelTest, unittest.TestCase):
        index = "trt1:trtspor:"

    class testtrtsporyildiz(ChannelTest, unittest.TestCase):
        minepg = 0
        index = "trt1:trtsporyildiz:"


except ImportError:
    pass


from liblivechannels import scraper
from scrapertools.multi import multi


class trt1(multi, scraper):
    title = u"TRT 1"
    icon = "https://www.trt1.com.tr/public/logo/d60ab555-f948-464a-a139-df5410d2a7b5/trt1_logo.png"
    categories = [u"Türkçe", u"Realiti"]
    yayin_id = "trt-1"
    ses_id = "trt1-izle"
    selcuk_name = "trt1"

    def get(self):
        yield "https://tv-trt1.live.trt.com.tr/master.m3u8"
        for stream in multi.get(self):
            yield stream


class trtspor(multi, scraper):
    title = u"TRT Spor"
    icon = "https://www.trtspor.com.tr/static/img/trtspor-logo-yeni.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_id = "trt-3"
    ses_id = "trt3-spor-izle"
    selcuk_name = "trtspor"


class trtsporyildiz(multi, scraper):
    title = u"TRT Spor Yildiz"
    icon = "https://www.trtspor.com.tr/static/img/trt-spor-yildiz-logo-beyaz-zemin.png"
    categories = [u"Türkçe", u"Spor"]
    kolay_id = "/trt-spor-2/1"
