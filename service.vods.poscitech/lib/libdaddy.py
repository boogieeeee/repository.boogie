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
dtrgx = "([0-9]{2})[\sa-zA-Z]+(january|february|march|april|may|june|july|august|october|november|december)\s+([0-9]{4}).+?GMT\+([0-9]+)"

monthtoint = {"january": 1,
              "february": 2,
              "march": 3,
              "april": 4,
              "may": 5,
              "june": 6,
              "july": 7,
              "august": 8,
              "october": 9,
              "november": 10,
              "september": 11,
              "december": 12}


def geturl(streamid):
    u = "%s/embed/stream-%s.php" % (domain, streamid)
    xiframe = htmlement.fromstring(net.http(u, referer=domain))
    iframeu = xiframe.find(".//iframe[@id='thatframe']").get("src")
    iframe = net.http(iframeu, referer=u)
    iframeu2 = re.search("iframe\s*?src=(?:\'|\")(.+?)(?:\'|\")", iframe).group(1)
    iframe = net.http(iframeu2, referer=iframeu)
    src = re.findall(mrgx, iframe)
    ref = parse.urlparse(iframeu2)
    ref = "%s://%s/" % (ref.scheme, ref.netloc)
    return net.hlsurl(src[-1], headers={"Referer": ref}, adaptive=False)


def getschdate(page):
    dtmatch = re.search(dtrgx, page, re.IGNORECASE)
    day = int(dtmatch.group(1))
    month = monthtoint[dtmatch.group(2).lower().strip()]
    year = int(dtmatch.group(3))
    tz = tools.tz_utc()
    tz.settimezone(int(dtmatch.group(4)))
    dtob = datetime(day=day, month=month, year=year, tzinfo=tz)
    return dtob


def getevents():
    events = []
    page = net.http(domain)
    lines = page.split("\n")
    sch_date = getschdate(page)
    loctz = tools.tz_local()
    for lineno, line in enumerate(lines):
        sport = re.search("<h4><span.+?>(.+?)<", line)
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
    page = net.http(domain + "/24-hours-channels.php", cache=60 * 24)
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