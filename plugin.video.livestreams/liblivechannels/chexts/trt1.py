# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testtrt1(ChannelTest, unittest.TestCase):
        index = "trt1:trt1:"

    class testtrtspor(ChannelTest, unittest.TestCase):
        index = "trt1:trtspor:"

    class testtrtsporyildiz(ChannelTest, unittest.TestCase):
        index = "trt1:trtsporyildiz:"

    class testtrthaber(ChannelTest, unittest.TestCase):
        index = "trt1:trthaber:"
        
    class testtrtcocuk(ChannelTest, unittest.TestCase):
        index = "trt1:trtcocuk:"

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi


class trt1(multi, scraper):
    title = u"TRT 1"
    icon = "https://www.trt1.com.tr/public/logo/d60ab555-f948-464a-a139-df5410d2a7b5/trt1_logo.png"
    categories = [u"Türkçe", u"Realiti"]
    yayin_id = "trt-1"
    selcuk_name = "trt1"
    kolay_ids = ["/trt-1-canli/1", "/trt-1-canli/2", "/trt-1-canli/3", "/trt-1-canli/4"]
    canlitv_ids = ["trt-1-canli-izle/1", "trt-1-canli-izle/2"]
    selcuk_adaptive = False


class trtspor(multi, scraper):
    title = u"TRT Spor"
    icon = "https://www.trtspor.com.tr/static/img/trtspor-logo-yeni.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_id = "trt-3"
    selcuk_name = "trtspor"
    kolay_ids = ["/trt-spor/1", "/trt-spor/3"]
    canlitv_ids = ["trt-spor", "trt-spor/2", "trt-spor/3"]
    selcuk_adaptive = False


class trtsporyildiz(multi, scraper):
    title = u"TRT Spor Yildiz"
    icon = "https://www.trtspor.com.tr/static/img/trt-spor-yildiz-logo-beyaz-zemin.png"
    categories = [u"Türkçe", u"Spor"]
    kolay_ids = "/trt-spor-yildiz/1", "/trt-spor-yildiz/2"
    canlitv_ids = "trt-spor-yildiz/1", "trt-spor-yildiz/2", "trt-spor-yildiz/3"
    # selcuk_name = "trtspor2"
    mynet_yayin = "trt-spor-yildiz"
    

class trthaber(multi, scraper):
    title = u"TRT Haber"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/TRT_Haber_Eyl%C3%BCl_2020_Logo.svg/2560px-TRT_Haber_Eyl%C3%BCl_2020_Logo.svg.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_id = "trt-haber"
    youtube_chanid = "trthaber"
    kolay_ids = ["/trt-haber/1", "/trt-haber/2", "/trt-haber/3", "/trt-haber/4"]
    canlitv_ids = ["trt-haber/1", "trt-haber/2"]
    

class trtcocuk(multi, scraper):
    title = u"TRT Çocuk"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/TRT_%C3%87ocuk_logo_%282021%29.svg/2560px-TRT_%C3%87ocuk_logo_%282021%29.svg.png"
    categories = [u"Türkçe", u"Çocuk"]
    yayin_id = "trt-cocuk"
    kolay_ids = ["/trt-cocuk/1", "/trt-cocuk/2"]
    canlitv_ids = ["trt-cocuk/1", "trt-cucuk/2", "trt-cocuk/3"]
