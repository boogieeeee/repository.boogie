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
mrgx = "source\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")"
dtrgx = "([0-9]{1,2})[\sa-zA-Z]*?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-zA-Z\s]*?([0-9]{4})"

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
    u = "%s/embed/stream-%s.php" % (domain, streamid)
    xiframe = htmlement.fromstring(net.http(u, referer=domain))
    iframeu = xiframe.find(".//iframe[@id='thatframe']").get("src")
    iframe = net.http(iframeu, referer=u)
    src = re.findall(mrgx, iframe)
    ref = parse.urlparse(iframeu)
    host = re.search(",'([a-zA-Z0-9\.\-]+?)'\);", iframe).group(1)
    orig = "%s://%s" % (ref.scheme, ref.netloc)
    ref = "%s://%s/" % (ref.scheme, ref.netloc)
    headers={"Host": host,
             "Origin": orig,
             "Referer": ref}
    return mediaurl.hlsurl(src[-1], headers=headers, adaptive=True, ffmpegdirect=False,
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
    schedules = ["schedule-extra-generated.json", "schedule-generated.json", "extra2-schedule.php"]
    for schedule in schedules:
        js = net.http(f"{domain}/schedule/{schedule}", json=True)
        for dt, members in js.items():
            sch_date = getschdate(dt)
            for category, events in members.items():
                for event in events:
                    title = event["event"]
                    evdtmatch = re.search("([0-9]{1,2})\:([0-9]{1,2})(.+)", event["time"])
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
    return allevents


def getchmeta(numbyname=False, nameidbynum=False):
    page = net.http(domain + "/24-7-channels.php", cache=60 * 24)
    chnames = {}
    for a in htmlement.fromstring(page).iterfind(".//div[@class='grid-item']/a"):
        href = a.get("href")
        if href is not None:
            chnum = re.search("stream\-([0-9]+)\.", href)
            if chnum:
                chnum = int(chnum.group(1))
                if numbyname:
                    chnames[chnum] = tools.elementsrc(a)
                elif nameidbynum:
                    chnames[tools.elementsrc(a).lower().replace(" ", "").strip()] = chnum
    return chnames
