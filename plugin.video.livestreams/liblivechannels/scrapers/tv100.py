# -*- coding: utf-8 -*-


from liblivechannels import scraper
from scrapertools import youtube


class tv100(scraper):
    title = u"TV 100"
    categories = ["Turkish", "Turkey", "News"]
    icon = "https://s.tv100.com/assets/web/images/logo.png"
    yid = "9NMCgLjGVRU"

    def get(self):
        for media in youtube.ydl().geturls("https://www.youtube.com/watch?v=%s" % self.yid):
            yield media
