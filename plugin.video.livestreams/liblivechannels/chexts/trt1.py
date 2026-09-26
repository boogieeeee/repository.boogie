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
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/TRT_1_logo_%282020-2021%29.svg/960px-TRT_1_logo_%282020-2021%29.svg.png"
    categories = [u"Türkçe", u"Realiti"]
    yayin_name = "trt1"
    canlitvcenter_name = "trt 1"
    canlitvme_name = "TRT 1"
    acestreams = ["acestream://d4384fd1b8d17bb4e31e60c9edce0c4a8f3fe1fb"]


class trtspor(multi, scraper):
    title = u"TRT Spor"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/TRT_Spor_logo_%282022%29.svg/640px-TRT_Spor_logo_%282022%29.svg.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "trtspor"
    canlitvme_name = "TRT Spor"
    canlitvcenter_name = "trt spor"
    acestreams = ["acestream://6c5e9bcc44d40423acfa5870a173c98213754af7"]


class trtsporyildiz(multi, scraper):
    title = u"TRT Spor Yildiz"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/TRT_Spor_Y%C4%B1ld%C4%B1z_Logo.svg/960px-TRT_Spor_Y%C4%B1ld%C4%B1z_Logo.svg.png"
    categories = [u"Türkçe", u"Spor"]
    canlitvme_name = "TRT Spor Yıldız"
    yayin_name = "TRT SPOR YILDIZ"
    canlitvcenter_name = "TRT Spor Yıldız"


class trthaber(multi, scraper):
    title = u"TRT Haber"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/TRT_Haber_Eyl%C3%BCl_2020_Logo.svg/2560px-TRT_Haber_Eyl%C3%BCl_2020_Logo.svg.png"
    categories = [u"Türkçe", u"Haber"]
    yayin_name = "trthaber"
    youtube_chanid = "trthaber"
    canlitvcenter_name = "trt haber"
    canlitvme_name = "TRT Haber"
    directs = [mediaurl.HlsUrl("https://tv-trthaber.medya.trt.com.tr/master.m3u8")]
    acestreams = ["acestream://6f21947257ff458ca0cdaa51d38adf822661c40c"]


class trtcocuk(multi, scraper):
    title = u"TRT Çocuk"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/TRT_%C3%87ocuk_logo_%282021%29.svg/2560px-TRT_%C3%87ocuk_logo_%282021%29.svg.png"
    categories = [u"Türkçe", u"Çocuk"]
    yayin_name = "trtcocuk"
    canlitvcenter_name = "TRT Çocuk"
    canlitvme_name = "TRT Çocuk"
    directs = [mediaurl.HlsUrl("https://tv-trtcocuk.medya.trt.com.tr/master.m3u8")]
    acestreams = ["acestream://0e2e97a02f65bc6820e402331028489f0dcdfd49"]


class trtbelgesel(multi, scraper):
    title = u"TRT Belgesel"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/TRT_Belgesel_kurumsal_logo_%282015-2019%29.png/800px-TRT_Belgesel_kurumsal_logo_%282015-2019%29.png"
    categories = [u"Türkçe", u"Belgesel"]
    yayin_name = "trtbelgesel"
    canlitvcenter_name = "trt belgesel"
    canlitvme_name = "TRT Belgesel"
    acestreams = ["acestream://811c3c90eb249d1cf65502848d395ac9d6de3529"]
