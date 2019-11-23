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
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from liblivechannels import scraper
import re


class youtube(object):
    domain = "https://www.youtube.com"
    yid = None
    h = {"Cookie": "PREF=f1=50000000"}
    
    def checkerrors(self):
        if self.yid:
            return "ID not provided"

    def checkalive(self):
        if not self.yid:
            u = "%s/channel/%s" % (self.domain, self.chanid)
            page = self.vods.download(u, referer=self.domain, headers=self.h)
            vids = re.search('videoId":"(.+?)"', page)
            self.yid = vids.group(1)
        return self.yid

    def get(self):
        if not self.yid and not self.yid == -1:
            self.checkalive()
        yield "%s/watch?v=%s" % (self.domain, self.yid)


class startv(youtube, scraper):
    title = "Star TV"
    categories = ["Youtube", "Turkish", "Turkey", "Entertainment"]
    chanid = "UCsFINj3y7SjBaeUxiSdRjlA"
    icon = "https://yt3.ggpht.com/-X-RYL1PddXc/AAAAAAAAAAI/AAAAAAAAAAA/hi1PIZ9nWEU/s288-c-k-no-mo-rj-c0xffffff/photo.jpg"


class tgrthaber(youtube, scraper):
    title = "TGRT Haber"
    categories = ["Youtube", "Turkish", "Turkey", "News"]
    chanid = "UCzgrZ-CndOoylh2_e72nSBQ"
    icon = "https://yt3.ggpht.com/-gHBfX_GHj34/AAAAAAAAAAI/AAAAAAAAAAA/ysnSlN6cxKA/s288-c-k-no-mo-rj-c0xffffff/photo.jpg"


class tvnet(youtube, scraper):
    title = "TvNET"
    categories = ["Youtube", "Turkish", "Turkey", "News"]
    chanid = "UC8rh34IlJTN0lDZlTwzWzjg"
    icon = "https://yt3.ggpht.com/-Kt-wthe5iBE/AAAAAAAAAAI/AAAAAAAAAAA/zzHGNepapnc/s288-c-k-no-mo-rj-c0xffffff/photo.jpg"


class ntv(youtube, scraper):
    title = "NTV"
    categories = ["Youtube", "Turkish", "Turkey", "News"]
    yid = "XEJM4Hcgd3M"
    icon = "https://ntv.com.tr/content/img/logo.png"

class tv100(youtube, scraper):
    title = "tv100"
    categories = ["Youtube", "Turkish", "Turkey", "News"]
    yid = "9NMCgLjGVRU"
    icon = "https://s.tv100.com/assets/web/images/logo.png"
