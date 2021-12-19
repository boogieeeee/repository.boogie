# -*- encoding: utf-8 -*-
'''
Created on Dec 19, 2021

@author: boogie
'''
from tinyxbmc import net
from tinyxbmc import tools
import datetime
import re
import htmlement
from liblivechannels import programme


url = "https://www.mynet.com/tv-rehberi/%s-yayin-akisi-%s"
suffixes = "bugun", "yarin", "sonraki-gun"
trmonmap = {"ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6, "temmuz": 7,
            "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12}
trtz = tools.tz_utc()
utctz = tools.tz_utc()
trtz.settimezone(3)

now = datetime.datetime.now()
now = now.astimezone(trtz)


def iterprogrammes(channame):
    prename = predate = None
    for i in range(len(suffixes)):
        pagex = htmlement.fromstring(net.http(url % (channame, suffixes[i])))
        curtxt = pagex.find(".//a[%d]/div[@class='day-date']" % (i + 1)).text
        m1 = re.search("([0-9]+)\s(.+)", curtxt)
        curd = int(m1.group(1))
        curm = trmonmap[m1.group(2).lower().strip()]
        for li in pagex.iterfind(".//div[@class='container']/div/ul/li"):
            ptime = li.find(".//strong")
            pname = li.find(".//p")
            if ptime is not None and pname is not None:
                phour, pmin = ptime.text.split(":")
                phour = int(phour)
                pmin = int(pmin)
                pname = pname.text.strip()
                if pname == "-":
                    continue
                pdate = datetime.datetime(day=curd, month=curm, year=now.year,
                                          hour=phour, minute=pmin, tzinfo=trtz)
                if prename:
                    yield programme(prename, predate, pdate)
                prename = pname
                predate = pdate
