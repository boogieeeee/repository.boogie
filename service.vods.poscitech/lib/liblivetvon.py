'''
Created on Jun 6, 2022

@author: boogie
'''
import htmlement
import re
from datetime import datetime, timedelta
from tinyxbmc.addon import kodisetting
from tinyxbmc import net
from tinyxbmc import mediaurl
from tinyxbmc import tools
from six.moves.urllib import parse


setting = kodisetting("service.vods.poscitech")
domain = "https://" + setting.getstr("domain")
dtrgx = r"([0-9]{1,2})[\sa-zA-Z]*?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-zA-Z\s]*?([0-9]{4})"

monthtoint = {"jan": 1,
              "feb": 2,
              "mar": 3,
              "apr": 4,
              "may": 5,
              "jun": 6,
              "jul": 7,
              "aug": 8,
              "oct": 9,
              "nov": 10,
              "sep": 11,
              "dec": 12}


def geturl(streamid):
    u = "%s/stream/stream-%s.php" % (domain, streamid)
    xiframe = htmlement.fromstring(net.http(u, referer=domain))
    iframeu = xiframe.find(".//iframe[@id='thatframe']").get("src")
    iframe = net.http(iframeu, referer=u)
    vars = {"channelKey": "",
            "authTs": "",
            "authRnd": "",
            "authSig": "",}
    for k, v in vars.items():
        vars[k] = re.search(f"var\s+{k}\s+=\s+(?:\"|\')(.+?)(?:\"|\');", iframe).group(1)
    authurl = re.search(r"(?:\"|\')(.+?auth\.php.*?)\?", iframe).group(1)
    params = {"channel_id": vars["channelKey"],
              "ts": vars["authTs"],
              "rnd": vars["authRnd"],
              "sig": vars["authSig"]}
    auth = net.http(net.absurl(authurl, iframeu), params=params, json=True)
    lookupurl = authurl = re.search(r"(?:\"|\')(.+?server_lookup\.php.*?)\?", iframe).group(1)
    params = {"channel_id": vars["channelKey"]}
    lookup = net.http(net.absurl(lookupurl, iframeu), params=params, json=True)
    server_key = lookup["server_key"]
    pre = server_key.split("/")[0]
    post = server_key
    murl = f"https://{pre}new.newkso.ru/{post}/{vars['channelKey']}/mono.m3u8"
    
    iframeu_p = parse.urlparse(iframeu)
    orig = iframeu_p.scheme + "://" + iframeu_p.netloc
    headers={
             "Origin": orig,
             "Referer": orig + "/",
             }
    return mediaurl.hlsurl(murl, headers=headers, adaptive=True, ffmpegdirect=False,
                           lurl="", lheaders=headers, lbody="", lresponse="", license=None)


def getschdate(page):
    today =  datetime.now()
    for dtmatch in re.finditer(dtrgx, page, re.IGNORECASE): 
        day = int(dtmatch.group(1))
        month = monthtoint[dtmatch.group(2).lower().strip()]
        year = int(dtmatch.group(3))
        tz = tools.tz_utc()
        tz.settimezone(1)
        dtob = datetime(day=day, month=month, year=year, tzinfo=tz)
        return dtob
    return today

def getevents():
    allevents = []
    loctz = tools.tz_local()
    schedules = ["schedule-extra-generated.php", "schedule-generated.php", "extra2-schedule-2.php"]
    for schedule in schedules:
        js = net.http(f"{domain}/schedule/{schedule}", referer=domain, json=True)
        for dt, members in js.items():
            sch_date = getschdate(dt)
            for category, events in members.items():
                category = re.sub(r"<.*?>", "", category).strip()
                for event in events:
                    title = event["event"]
                    evdtmatch = re.search(r"([0-9]{1,2})\:([0-9]{1,2})(.*)", event["time"])
                    hour = int(evdtmatch.group(1))
                    minute = int(evdtmatch.group(2))
                    evdate = datetime(hour=hour, minute=minute,
                                      year=sch_date.year, month=sch_date.month, day=sch_date.day,
                                      tzinfo=sch_date.tzinfo)
                    channels = []
                    for channel in event["channels"]:
                        if(channel["channel_id"]).isdigit():
                            channels.append([channel["channel_name"], int(channel["channel_id"])])
                    allevents.append([evdate.astimezone(loctz), category, title, channels])
    allevents.sort()
    return allevents


def getchmeta(numbyname=False, nameidbynum=False):
    page = net.http(domain + "/24-7-channels.php", cache=60 * 24)
    chnames = {}
    for a in htmlement.fromstring(page).iterfind(".//div[@class='grid-item']/a"):
        href = a.get("href")
        if href is not None:
            chnum = re.search(r"stream\-([0-9]+)\.", href)
            if chnum:
                chnum = int(chnum.group(1))
                if numbyname:
                    chnames[chnum] = tools.elementsrc(a)
                elif nameidbynum:
                    chnames[tools.elementsrc(a).lower().replace(" ", "").strip()] = chnum
    return chnames
