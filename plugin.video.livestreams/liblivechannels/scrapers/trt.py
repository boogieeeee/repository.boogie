# -*- encoding: utf-8 -*-
from liblivechannels import scraper


class trt1(scraper):
    title = u"TRT 1"
    icon = "https://www.trt1.com.tr/public/logo/d60ab555-f948-464a-a139-df5410d2a7b5/trt1_logo.png"
    categories = [u"Türkçe", u"Realiti"]
    ushlsproxy = False

    def get(self):
        yield "https://tv-trt1.live.trt.com.tr/master.m3u8"
