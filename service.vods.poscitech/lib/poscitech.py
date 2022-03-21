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
from six.moves.urllib import parse


# references: "https://poscitech.club/tv/ch1.php, https://daddylive.me/"

dom = "https://daddylive.me"
mrgx = "source\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")"


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
        page = self.download(dom)
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
            page = self.download(dom + "/24-hours-channels.php")
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
        u = "%s/embed/stream-%s.php" % (dom, streamid)
        print(u)
        iframeu = htmlement.fromstring(net.http(u)).find(".//iframe[@id='thatframe']").get("src")
        iframe = net.http(iframeu, referer=u)
        iframeu2 = re.search("iframe\s*?src=(?:\'|\")(.+?)(?:\'|\")", iframe).group(1)
        iframe = net.http(iframeu2, referer=iframeu)
        src = re.findall(mrgx, iframe)
        ref = parse.urlparse(iframeu2)
        ref = "%s://%s/" % (ref.scheme, ref.netloc)
        yield net.hlsurl(src[-1], headers={"Referer": ref}, adaptive=False)
