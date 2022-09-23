'''
Created on Jun 6, 2022

@author: boogie
'''
import htmlement
import re
from datetime import datetime, timedelta
from tinyxbmc.addon import kodisetting
from tinyxbmc import net
from tinyxbmc import tools
from six.moves.urllib import parse


setting = kodisetting("service.vods.poscitech")
domain = "https://" + setting.getstr("domain")
mrgx = "source\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")"
dtrgx = "([0-9]{1,2})[\sa-zA-Z]*?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*?([0-9]{4})"

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
    ref = "%s://%s/" % (ref.scheme, ref.netloc)
    return net.hlsurl(src[-1], headers={"Referer": ref}, adaptive=False)


def getschdate(page):
    dtmatch = re.search(dtrgx, page, re.IGNORECASE)
    day = int(dtmatch.group(1))
    month = monthtoint[dtmatch.group(2).lower().strip()]
    year = int(dtmatch.group(3))
    tz = tools.tz_utc()
    tz.settimezone(1)
    dtob = datetime(day=day, month=month, year=year, tzinfo=tz)
    return dtob


def getevents():
    events = []
    page = net.http(domain)
    lines = page.split("\n")
    sch_date = getschdate(page)
    loctz = tools.tz_local()
    for lineno, line in enumerate(lines):
        sport = re.search("<h2 style.+?>(.+?)<", line)
        if sport:
            prevhour = -1
            for m in re.finditer("hr\>(.+?)\<(.+?)(?:<\/p|<br\s\/>)", lines[lineno + 1]):
                title = m.group(1)
                print(title)
                evdtmatch = re.search("([0-9]{2})\:([0-9]{2})(.+)", title)
                title = evdtmatch.group(3).strip()
                hour = int(evdtmatch.group(1))
                minute = int(evdtmatch.group(2))
                evdate = datetime(hour=hour, minute=minute,
                                  year=sch_date.year, month=sch_date.month, day=sch_date.day,
                                  tzinfo=sch_date.tzinfo)
                if prevhour > hour:
                    evdate = evdate + timedelta(hours=24)
                prevhour = hour
                txt = m.group(2)
                channels = []
                for m in re.finditer("\<a.+?\>(.+?)\<\/a\>", txt):
                    chnum = re.search("\(CH\-([0-9]+)\)", m.group(1))
                    if chnum:
                        chnum = int(chnum.group(1))
                        channels.append((m.group(1), chnum))
                if channels:
                    events.append([evdate.astimezone(loctz), sport.group(1), title, channels])
    return events


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
