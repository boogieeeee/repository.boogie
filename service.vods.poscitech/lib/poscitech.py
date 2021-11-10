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
from tinyxbmc import net
from tinyxbmc import const
from tinyxbmc import tools


# references: "https://poscitech.club/tv/ch1.php, https://daddylive.me/"

sdom = "https://www.eplayer.to/"
surl = sdom + "poscitech.php?live=%s&vw=100vw&vh=100vh"
referer = "https://poscitech.club/"
rgx = "source\s*?\:\s*?(?:\"|\")(.+?)(?:\"|\")"
ddom = "https://daddylive.me/"


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
        page = self.download(ddom)
        for m in re.finditer("hr\>(.+?)\<(.+?)(?:<\/p|<br\s\/>)", page):
            title = m.group(1)
            txt = m.group(2)
            channels = []
            for m in re.finditer("\<a.+?\>(.+?)\<\/a\>", txt):
                chnum = re.search("\(CH\-([0-9]+)\)", m.group(1))
                if chnum:
                    chnum = int(chnum.group(1))
                    channels.append((m.group(1), chnum))
            if channels:
                self.additem(title, channels)

    def getmovies(self, cat=None):
        if cat:
            for ctxt, cnum in cat:
                self.additem(ctxt, cnum)
        else:
            page = self.download(ddom + "/24-hours-channels.php")
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
        url = surl % streamid
        page = self.download(url, referer=referer)
        m3 = re.search(rgx, page).group(1)
        yield net.tokodiurl(m3, headers={"Referer": sdom, "User-Agent": const.USERAGENT})
