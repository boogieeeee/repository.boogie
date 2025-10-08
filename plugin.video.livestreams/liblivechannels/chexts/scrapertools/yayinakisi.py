# -*- encoding: utf-8 -*-
'''
Created on Feb 1, 2021

@author: boogie
'''
import re
import json
import htmlement
from datetime import datetime, timedelta

from tinyxbmc import net
from tinyxbmc import tools

from liblivechannels import programme
from liblivechannels.chexts.scrapertools import normalize


domain = "https://www.tvyayinakisi.com/"
TZ = 3
TRTZ = tools.tz_utc()
TRTZ.settimezone(TZ)
LOCTZ = tools.tz_local()


def find(chname):
    xpage = htmlement.fromstring(net.http("%s/tv-kanallari" % domain, cache=60))
    for channel in xpage.iterfind(".//li[@class='channel-item']"):
        name = channel.get("data-name")
        if not name:
            continue
        if normalize(name) == normalize(chname):
            return channel.find(".//a").get("href")


def todate(txt, dayoffset):
    dt = datetime.now(LOCTZ)
    dt = dt.astimezone(TRTZ).replace(second=0, microsecond=0)
    hour, minute = [int(x.strip()) for x in txt.split(":")]
    offset = timedelta(days=dayoffset)
    return dt.replace(hour=hour, minute=minute, tzinfo=TRTZ) + offset


def iterprogrammes(chname=None, chid=None):
    link = None
    if chid:
        link = "%s%s-yayin-akisi" % (domain, chid)
    elif chname:
        link = find(chname)
    if link:
        subpage = htmlement.fromstring(net.http(link, referer=domain, cache=5))
        prevdate = None
        prevtitle = None
        dayoffset = 0
        for day in subpage.iterfind(".//div[@role='region']"):
            for prog in day.iterfind('.//li[@itemprop="itemListElement"]'):
                pdate = todate(tools.elementsrc(prog.find(".//time")), dayoffset)
                ptitle = prog.find(".//div[@class='title']").text.strip()
                if prevdate:
                    yield programme(prevtitle,
                                    prevdate,
                                    pdate)
                prevdate = pdate
                prevtitle = ptitle
            dayoffset += 1
