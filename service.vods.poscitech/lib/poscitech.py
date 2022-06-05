# -*- coding: utf-8 -*-
'''
    Author    : Huseyin BIYIK <husenbiyik at hotmail>
    Year      : 2016
    License   : GPL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more detail```    s.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import vods
import re
import htmlement
from datetime import datetime, timedelta
from tinyxbmc import net
from tinyxbmc import const
from tinyxbmc import tools
from six.moves.urllib import parse


# references: "https://poscitech.club/tv/ch1.php, https://daddylive.me/"

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


def getschdate(page):
    dtmatch = re.search(dtrgx, page, re.IGNORECASE)
    day = int(dtmatch.group(1))
    month = monthtoint[dtmatch.group(2).lower().strip()]
    year = int(dtmatch.group(3))
    tz = tools.tz_utc()
    tz.settimezone(int(dtmatch.group(4)))
    dtob = datetime(day=day, month=month, year=year, tzinfo=tz)
    return dtob

class poscitech(vods.movieextension):
    usedirect = True
    useaddonplayers = False
    uselinkplayers = False
    dropboxtoken = const.DB_TOKEN

    info = {"title": "DaddyLive"
            }
    art = {"icon": "https://i.imgur.com/8EL6mr3.png",
           "thumb": "https://i.imgur.com/8EL6mr3.png",
           "poster": "https://i.imgur.com/8EL6mr3.png"
           }

    def getcategories(self):
        events = []
        page = self.download("https://" + self.setting.getstr("domain"))
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
        for evdate, sport, title, channels in sorted(events):
            title = "%02d.%02d %02d:%02d | %s | %s" % (evdate.day, evdate.month, evdate.hour, evdate.minute,
                                                    sport, title)
            self.additem(title, channels)                
    def getmovies(self, cat=None):
        if cat:
            for ctxt, cnum in cat:
                self.additem(ctxt, cnum)
        else:
            page = self.download("https://" + self.setting.getstr("domain") + "/24-hours-channels.php")
            chnames = {}
            for a in htmlement.fromstring(page).iterfind(".//table/.//a"):
                href = a.get("href")
                if href is not None:
                    chnum = re.search("stream\-([0-9]+)\.", href)
                    if chnum:
                        chnames[int(chnum.group(1))] = tools.elementsrc(a)
            for i in range(1, 150 + 1):
                chname = chnames.get(i, "Channel")
                self.additem("%s (#%s)" % (chname, i), i)

    def geturls(self, streamid):
        u = "https://%s/embed/stream-%s.php" % (self.setting.getstr("domain"), streamid)
        xiframe = htmlement.fromstring(net.http(u, referer="https://" + self.setting.getstr("domain")))
        iframeu = xiframe.find(".//iframe[@id='thatframe']").get("src")
        iframe = net.http(iframeu, referer=u)
        iframeu2 = re.search("iframe\s*?src=(?:\'|\")(.+?)(?:\'|\")", iframe).group(1)
        iframe = net.http(iframeu2, referer=iframeu)
        src = re.findall(mrgx, iframe)
        ref = parse.urlparse(iframeu2)
        ref = "%s://%s/" % (ref.scheme, ref.netloc)
        yield net.hlsurl(src[-1], headers={"Referer": ref}, adaptive=False)
