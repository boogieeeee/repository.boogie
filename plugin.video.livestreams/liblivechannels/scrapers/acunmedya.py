# -*- encoding: utf-8 -*-
from liblivechannels import scraper
from tinyxbmc import tools
from scrapertools import yayinakisi
import re

import htmlement

import scrapertools


class tv8(scraper):
    domain = "https://www.tv8.com.tr"
    m3u8 = None
    title = u"S SPORT HD"
    icon = "https://img.tv8.com.tr/s/template/v2/img/tv8-logo.png"
    categories = [u"Türkçe", u"Realiti"]
    ushlsproxy = False

    def get(self):
        yield "https://tv8.personamedia.tv/tv8hls?fmt=hls"

    def iterprogrammes(self):
        for prog in yayinakisi.iterprogramme(self.title):
            yield prog

    def iterprogrammes2(self):
        piter = scrapertools.makeprograms()
        page = self.download("%s/yayin-akisi" % self.domain, referer=self.domain, timeout=10)
        tree = htmlement.fromstring(page)
        datestr = None
        for a in tree.findall(".//div[@id='hdtb-msb']/.//a"):
            a_class = a.get("class")
            if a_class is not None and "sd-active" in a_class:
                datestr = a.text.strip()
                break
        if not datestr:
            raise StopIteration
        localdate = re.search("([0-9]+)(.+?)([0-9]{4})", datestr)
        localday = int(localdate.group(1))
        localmonth = scrapertools.tr_months[unicode(localdate.group(2).strip().lower())]
        localyear = int(localdate.group(3))
        datepsr = scrapertools.dateparser(3, localyear, localmonth, localday, shiftdate=False)
        oldhour = 0
        dayshift = 0
        # xpath does not parse, use regex
        for tr in tree.iterfind(".//tr"):
            img = tr.find(".//td[@class='stream-img']/.//img").get("data-original")
            hour, minute = tr.find(".//td[@class='stream-time']/span").text.split(":")
            hour = int(hour.strip())
            if oldhour > hour:
                dayshift += 1
            oldhour = hour
            titletd = tr.find(".//td[@class='stream-name']")
            catspan = titletd.find(".//span")
            cats = []
            if catspan is not None:
                cats.append(catspan.text)
            title = tools.strip(tools.elementsrc(titletd, [catspan]))
            yield piter.add(title, datepsr.datefromhour(hour, minute, daydelta=dayshift),
                            icon=img, categories=cats)
