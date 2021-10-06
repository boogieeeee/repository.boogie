'''
Created on Jul 23, 2021

@author: boogie
'''
from liblivechannels import programme
from tinyxbmc import net, tools
from datetime import datetime

import json

domain = "https://tv-guide.vercel.app"
imgdomain = "https://adma.tmsimg.com"
UTC = tools.tz_utc()


def iterprogrammes(tvid):
    u = "%s/api/stationAirings?stationId=%s" % (domain, tvid)
    for p in json.loads(net.http(u, referer=domain)):
        start = datetime.strptime(p["startTime"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=UTC)
        end = datetime.strptime(p["endTime"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=UTC)
        img = p["program"].get("preferredImage")
        if img:
            img = img.get("uri")
        if img:
            img = net.absurl(img, imgdomain)
        yield programme(p["program"]["title"],
                        start,
                        end,
                        desc=p["program"].get("longDescription", p["program"].get("shortDescription", None)),
                        icon=img)
