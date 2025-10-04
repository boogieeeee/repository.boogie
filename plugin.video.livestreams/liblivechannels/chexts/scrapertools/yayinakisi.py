# -*- encoding: utf-8 -*-
'''
Created on Feb 1, 2021

@author: boogie
'''
import re
import json
import htmlement
from datetime import datetime

from tinyxbmc import net
from tinyxbmc import tools

from liblivechannels import programme
from liblivechannels.chexts.scrapertools import normalize


domain = "https://www.tvyayinakisi.com/"
TZ = 3
trtz = tools.tz_utc()
trtz.settimezone(TZ)


def find(chname):
    xpage = htmlement.fromstring(net.http("%s/tv-kanallari" % domain, cache=60))
    for channel in xpage.iterfind(".//a[@class='channel-card']"):
        div = channel.find(".//div[@class='name']")
        if div is not None and normalize(tools.elementsrc(div)) == normalize(chname):
            return channel.get("href")


def todate(txt):
    if txt.count("T") == 2:
        txt = re.sub(r"T[0-9\:]+T", "T", txt)

    formats = ["%Y-%m-%dT%H:%M:%S",
               "%Y-%m-%d %H:%M:%S",
               "%Y-%m-%dT%H:%M",
               "%Y-%m-%d %H:%M"]
    for fmt in formats:
        try:
            dt = datetime.strptime(txt, fmt)
            return dt.replace(tzinfo=trtz)
        except ValueError:
            pass
    print("unknown time: %s" % txt)


def iterprogrammes(chname=None, chid=None):
    link = None
    if chid:
        link = "%s%s-yayin-akisi" % (domain, chid)
    elif chname:
        link = find(chname)
    if link:
        subpage = net.http(link, referer=domain, cache=5)
        apilink = re.search(r"kanal_detay\:\s?(?:\"|\')(.+?)(?:\"|\')", subpage)
        dslug = re.search(r"data-slug\=\s?(?:\"|\')(.+?)(?:\"|\')", subpage)
        if apilink and dslug:
            js = json.loads(net.http(apilink.group(1) + dslug.group(1), referer=domain))
            for i in range(len(js["content"])):
                try:
                    nextstart = todate(js["content"][i + 1]["brod_start"])
                except IndexError:
                    nextstart = None
                start = todate(js["content"][i]["brod_start"])
                end = todate(js["content"][i]["brod_end"])
                if nextstart is not None and (end is None or (end is not None and end <= start)):
                    end = nextstart
                if start and end:
                    yield programme(js["content"][i]["name"],
                                    start,
                                    end,
                                    categories=[js["content"][i]["type"], js["content"][i]["type2"]]
                                    )
