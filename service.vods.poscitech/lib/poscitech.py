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
from tinyxbmc import net
from tinyxbmc import const


# references: "https://poscitech.club/tv/ch1.php, https://daddylive.me/"

sdom = "https://www.eplayer.to/"
surl = sdom + "poscitech.php?live=%s&vw=100vw&vh=100vh"
referer = "https://poscitech.club/"
rgx = "source\s*?\:\s*?(?:\"|\")(.+?)(?:\"|\")"


class poscitech(vods.movieextension):
    usedirect = True
    useaddonplayers = False
    uselinkplayers = False

    info = {"title": "Poscitech"
            }

    def getmovies(self, cat=None):
        for i in range(1, 130 + 1):
            pass
            self.additem("Channel %s" % i, i)

    def geturls(self, streamid):
        url = surl % streamid
        page = self.download(url, referer=referer)
        m3 = re.search(rgx, page).group(1)
        yield net.tokodiurl(m3, headers={"Referer": sdom, "User-Agent": const.USERAGENT})
