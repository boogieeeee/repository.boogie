# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testssport1(ChannelTest, unittest.TestCase):
        index = "ssport:ssport1:"
        minlinks = 1

    class testssport2(ChannelTest, unittest.TestCase):
        index = "ssport:ssport2:"
        minlinks = 1

except ImportError:
    pass


from liblivechannels import scraper
from liblivechannels.chexts.scrapertools.multi import multi
from liblivechannels.chexts.scrapertools.mynetyayin import trmonmap, trtz, now
from liblivechannels import programme
import re
import datetime

from tinyxbmc import net
import htmlement


class ssport1(multi, scraper):
    title = u"S Sport 1"
    icon = "https://upload.wikimedia.org/wikipedia/tr/thumb/8/82/S_Sport_logo.jpg/800px-S_Sport_logo.png"
    categories = [u"Türkçe", u"Spor"]
    yayin_name = "ssport"
    selcuk_name = "ssport"

    def iterprogrammes(self):
        for prog in iterprogrammes(""):
            yield prog


class ssport2(multi, scraper):
    title = u"S Sport 2"
    icon = "https://upload.wikimedia.org/wikipedia/tr/thumb/e/ed/S_Sport_2_logo.jpg/800px-S_Sport_2_logo.png"
    categories = [u"Türkçe", u"Spor"]
    selcuk_name = "ssport2"

    def iterprogrammes(self):
        for prog in iterprogrammes("-2"):
            yield prog


def iterprogrammes(suffix):
    u = "https://www.ssport.tv/yayin-akisi"
    pagex = htmlement.fromstring(net.http(u))
    prename = predate = None
    for day in pagex.iterfind('.//ul[@id="switcher-day-s-sport%s"]/li' % suffix):
        datadate = day.get("data-date")
        if datadate is not None:
            curmatch = re.search(r"([0-9]+)\s(.+?)\s", datadate)
            curd = int(curmatch.group(1))
            curm = trmonmap[curmatch.group(2).lower().strip()]
            for prog in day.iterfind("./ul/li"):
                pdate = prog.find(".//time")
                pname = prog.find(".//h3")
                if pdate is not None and pname is not None:
                    phour, pmin = pdate.get("datetime").split(":")
                    pdate = datetime.datetime(day=curd, month=curm, year=now.year,
                                              hour=int(phour), minute=int(pmin), tzinfo=trtz)
                    pname = pname.text.strip()
                    if prename:
                        yield programme(prename, predate, pdate)
                    prename = pname
                    predate = pdate
