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
        
    class testtrtbelgesel(ChannelTest, unittest.TestCase):
        index = "trt1:trtbelgesel:"


except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi

from tinyxbmc import mediaurl


class trt1(multi, scraper):
    title = u"TRT 1"
    icon = "https://www.trt1.com.tr/public/logo/d60ab555-f948-464a-a139-df5410d2a7b5/trt1_logo.png"
    categories = [u"Türkçe", u"Realiti"]
    yayin_id = "trt-1"
    selcuk_name = "trt1"
    canlitv_ids = ["trt1-izle", "trt1-izle/2"]
    canltivme_name = "TRT 1"


class trtspor(multi, scraper):
    title = u"TRT Spor"
    icon = "https://www.trtspor.com.tr/static/img/trtspor-logo-yeni.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_id = "trt-3"
    selcuk_name = "trtspor"
    canlitvme_name = "TRT Spor"


class trtsporyildiz(multi, scraper):
    title = u"TRT Spor Yildiz"
    icon = "https://www.trtspor.com.tr/static/img/trt-spor-yildiz-logo-beyaz-zemin.png"
    categories = [u"Türkçe", u"Spor"]
    selcuk_name = "trtspor2"
    mynet_yayin = "trt-spor-yildiz"
    canlitvme_name = "TRT Spor Yıldız"
    

class trthaber(multi, scraper):
    title = u"TRT Haber"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/TRT_Haber_Eyl%C3%BCl_2020_Logo.svg/2560px-TRT_Haber_Eyl%C3%BCl_2020_Logo.svg.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_id = "trt-haber"
    youtube_chanid = "trthaber"
    canlitv_ids = ["trt-haber/1", "trt-haber/2"]
    canlitvme_name = "TRT Haber"
    

class trtcocuk(multi, scraper):
    title = u"TRT Çocuk"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/TRT_%C3%87ocuk_logo_%282021%29.svg/2560px-TRT_%C3%87ocuk_logo_%282021%29.svg.png"
    categories = [u"Türkçe", u"Çocuk"]
    yayin_id = "trt-cocuk"
    canlitv_ids = ["trt-cocuk/1", "trt-cucuk/2", "trt-cocuk/3"]
    canlitvme_name = "TRT Çocuk"
    
class trtbelgesel(multi, scraper):
    title = u"TRT Belgesel"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/TRT_Belgesel_kurumsal_logo_%282015-2019%29.png/800px-TRT_Belgesel_kurumsal_logo_%282015-2019%29.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_id = "trt-belgesel"
    canlitv_ids = ["trtbelgesel-canli/1", "trtbelgesel-canli/2", "trt-cocuk/3"]
    canlitvme_name = "TRT Belgesel"
    directs = [mediaurl.hlsurl("https://tv-trtbelgesel.medya.trt.com.tr/master.m3u8")] 
