# -*- encoding: utf-8 -*-


from liblivechannels import scraper
from tinyxbmc import tools
import htmlement
import json
import re
import scrapertools
from scrapertools import youtube

import ecanli


class ciner(object):
    xpath = './/div[@class="htplay_video"]'
    yid = None

    def checkalive(self):
        tree = htmlement.fromstring(self.download(self.live, referer=self.domain))
        for div in tree.findall(self.xpath):
            data = div.get("data-ht")
            if data:
                self.m3u8 = json.loads(data)["ht_stream_m3u8"]
        return self.m3u8

    def get(self):
        if self.yid:
            with tools.ignoreexception():
                for media in youtube.iteryoutube(self, "https://www.youtube.com/watch?v=%s" % self.yid):
                    yield media
        with tools.ignoreexception():
            if not self.m3u8:
                self.checkalive()
            yield self.m3u8
        for media in ecanli.iterexternal(self.download, self.title):
            yield media


class haberturk(ciner, scraper):
    domain = "https://www.haberturk.com/"
    live = "%s/canliyayin" % domain
    categories = ["Turkish", "Turkey", "News"]
    title = u"Haber Türk"
    icon = "https://lh3.googleusercontent.com/RHV4WLdQNalCG87rSH5Q60ZDEnHMg1_Az679Dg6DglSinOxdyD3W80VLpn7SlSjd1Q=w300"
    m3u8 = None
    yid = "s-KKgm4ysjk"

    def iterprogrammes(self):
        piter = scrapertools.makeprograms()
        page = self.download("%stv/yayinakisi" % self.domain, referer=self.domain, timeout=10)
        localdate = re.search("rel=\"([0-9]{2})(.+?)([0-9]{4})\"", page)
        localday = int(localdate.group(1))
        localmonth = scrapertools.tr_months[unicode(localdate.group(2).strip().lower())]
        localyear = int(localdate.group(3))
        datepsr = scrapertools.dateparser(3, localyear, localmonth, localday, shiftdate=False)
        oldhour = 0
        dayshift = 0
        # xpath does not parse, use regex
        rgx = '<span class=\"programListLeft\">.+?<img src=\"(.+?)\".+?<span>([0-9\:]+?)</span>.+?<span>(.+?)</span>.+?<span>(.*?)</span>'
        records = re.finditer(rgx, page, re.DOTALL)
        for link in records:
            img = unicode(link.group(1))
            hour, minute = link.group(2).split(":")
            hour = int(hour.strip())
            if oldhour > hour:
                dayshift += 1
            oldhour = hour
            title = unicode(link.group(3))
            desc = unicode(link.group(4))
            yield piter.add(title, datepsr.datefromhour(hour, minute, daydelta=dayshift),
                            icon=img, desc=tools.strip(desc, True))


class showtv(ciner, scraper):
    domain = "http://www.showtv.com.tr/"
    live = "%s/canli-yayin" % domain
    categories = ["Turkish", "Turkey", "Entertainment"]
    title = u"Show TV"
    icon = "https://yt3.ggpht.com/a/AGF-l7-pbSxRH989aWGOuLgMyn41zkxdi-GTUlbfqA=s288-mo-c-c0xffffffff-rj-k-no"
    m3u8 = None
    xpath = xpath = './/div[@class="htplay"]'

    """
    def iterprogrammes(self):
        datepsr = scrapertools.dateparser(3, shiftdate=False)
        piter = scrapertools.makeprograms()
        page = self.download("%syayin-akisi" % (self.domain))
        oldhour = 0
        dayshift = 0
        # xpath does not parse, use regex
        rgx = "<figure>.+?<img.+?data-src=\"(.+?)\".+?<span class=\"title\">(.+?)</span>.+?class=\"description\">(.+?)</.+?<span>([0-9]+)</span>.+?<span>([0-9\:]+)</span>"
        for figure in re.finditer(rgx, page, re.DOTALL):
            img = unicode(figure.group(1))
            title = unicode(figure.group(2))
            desc = unicode(figure.group(3))
            hour = int(unicode(figure.group(4)))
            minute = figure.group(5).replace(":", "")
            if oldhour > hour:
                dayshift += 1
            oldhour = hour
            yield piter.add(title, datepsr.datefromhour(hour, minute, daydelta=dayshift), icon=img, desc=desc)
    """


class bloobmberght(ciner, scraper):
    domain = "http://www.bloomberght.com"
    live = "%s/tv" % domain
    categories = ["Turkish", "Turkey", "News", "Finance"]
    title = u"Bloomberg HT"
    icon = "http://www.bloomberght.com/images/logo.png"
    m3u8 = None

    """
    def iterprogrammes(self):
        datepsr = scrapertools.dateparser(3, shiftdate=False)
        piter = scrapertools.makeprograms()
        tree = htmlement.fromstring(self.download("%s/yayinakisi" % (self.domain)))
        oldhour = 0
        dayshift = - datepsr.loc_now.weekday()
        for figure in tree.iterfind(".//div[@class='swiper-wrapper']/div"):
            img = figure.find(".//img").get("src")
            hour, minute = figure.find(".//div[@class='time']").text.split(":")
            hour = int(hour.strip())
            if oldhour > hour:
                dayshift += 1
            oldhour = hour
            title = unicode(figure.find(".//h4").text)
            desc = unicode(tools.strip(figure.find(".//div[@class='detail']/p").text, True))
            yield piter.add(title, datepsr.datefromhour(hour, minute.strip(), daydelta=dayshift), icon=img, desc=desc)
    """
