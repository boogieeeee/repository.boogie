'''
Created on Jun 6, 2022

@author: boogie
'''
import htmlement
import re
import base64
import traceback
from datetime import datetime
from tinyxbmc.addon import kodisetting
from tinyxbmc import net
from tinyxbmc import mediaurl
from tinyxbmc import tools
from six.moves.urllib import parse
# from chromium import Browser


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

def get_forcedplay(xpage, iframeu, url):
    iframe = net.http(iframeu, referer=url)
    subiframe =  htmlement.fromstring(iframe).find(".//iframe[@id='thatframe']")
    if subiframe is not None:
        iframeu = subiframe.get("src")
        iframe = net.http(iframeu, referer=iframeu)
    jsvars = {"auth": "",
              "subdomain": "",
              "channelKey": "",
              "authTs": "",
              "authRnd": "",
              "authSig": "",}
    base64_map = {"__a": "subdomain",
                  "__b": "auth",
                  "__c": "authTs",
                  "__d": "authRnd",
                  "__e": "authSig"}
    for k, v in base64_map.items():
        val = re.search(f"var\s+{k}\s+=\s+atob\((?:\"|\')(.+?)(?:\"|\')\);", iframe).group(1)
        jsvars[v] = base64.b64decode(val).decode()
    jsvars["channelKey"] =  re.search(r"var\s+channelKey\s+=\s+(?:\"|\')(.+?)(?:\"|\')\;", iframe).group(1)
    params = {"channel_id": jsvars["channelKey"],
              "ts": jsvars["authTs"],
              "rnd": jsvars["authRnd"],
              "sig": jsvars["authSig"]}
    _auth = net.http(f"{jsvars['subdomain']}/{jsvars['auth']}", params=params)
    lookupurl = authurl = re.search(r"(?:\"|\')(.+?server_lookup\.php.*?)\?", iframe).group(1)
    params = {"channel_id": jsvars["channelKey"]}
    lookup = net.http(net.absurl(lookupurl, iframeu), params=params, json=True)
    server_key = lookup["server_key"]
    pre = server_key.split("/")[0]
    post = server_key
    murl = f"https://{pre}new.newkso.ru/{post}/{jsvars['channelKey']}/mono.m3u8"
    
    iframeu_p = parse.urlparse(iframeu)
    orig = iframeu_p.scheme + "://" + iframeu_p.netloc
    headers={
             "Origin": orig,
             "Referer": orig + "/",
             }
    return mediaurl.hlsurl(murl, headers=headers, adaptive=False, ffmpegdirect=False,
                           lurl="", lheaders=headers, lbody="", lresponse="", license=None)


def geturl(streamid, path="/stream/stream-%s.php"):
    u = ("%s" + path) % (domain, streamid)
    xpage = htmlement.fromstring(net.http(u, referer=domain))
    iframes = xpage.findall(".//iframe")
    for cb in [get_forcedplay]:
        for iframe in iframes:
            iframeu = iframe.get("src")
            try:
                return cb(xpage, iframeu, u)
            except Exception:
                print(traceback.format_exc())


def getschdate(page):
    today =  datetime.now()
    for dtmatch in re.finditer(dtrgx, page, re.IGNORECASE): 
        day = int(dtmatch.group(1))
        month = monthtoint[dtmatch.group(2).lower().strip()]
        year = int(dtmatch.group(3))
        tz = tools.tz_utc()
        tz.settimezone(0)
        dtob = datetime(day=day, month=month, year=year, tzinfo=tz)
        return dtob
    return today

def getevents():
    allevents = []
    loctz = tools.tz_local()
    schedules = {"schedule-extra-generated.php": "/extra/stream-%s.php",
                 "schedule-generated.php": "/stream/stream-%s.php",
                 "extra2-schedule-2.php": "/stream/bet.php?id=%s"}
    for schedule, path in schedules.items():
        js = net.http(f"{domain}/schedule/{schedule}", referer=domain, json=True)
        for dt, members in js.items():
            sch_date = getschdate(dt)
            for category, events in members.items():
                category = re.sub(r"<.*?>", "", category).strip()
                if category == "All matches":
                    pass
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
                            name = f"{channel['channel_name']}({channel['channel_id']})"
                            channels.append([name, int(channel["channel_id"]), path])
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
