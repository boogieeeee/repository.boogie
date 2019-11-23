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
"""
from liblivechannels import scraper
import htmlement
import re


obselete, stream moved to youtube
class ntv(scraper):
    categories = ["Turkish", "News", "Turkey"]
    title = u"NTV"
    dataid = None
    domain = "https://www.ntv.com.tr"
    icon = "%s/content/img/logo.png" % domain

    def checkalive(self):
        page = self.vods.download(self.domain + "/canli-yayin/ntv", referer=self.domain)
        for div in htmlement.fromstring(page).findall(".//div[@data-player-token]"):
            token = div.get("data-player-token")
            src = div.get("data-player-mobile")
            if token and src:
                if src.startswith("//"):
                    src = "https:%s%s|Referer=%s" % (src, token, self.domain)
                self.dataid = src + token
                break
        return self.dataid

    def get(self):
        if not self.dataid:
            self.checkalive()
        yield self.dataid

channel closed
class ntvspor(scraper):
    categories = ["Turkish", "Sport", "Turkey"]
    title = u"NTV Spor"
    dataid = None
    domain = "https://www.ntvspor.net"
    icon = "%s/Content/dist/img/ntvspor-logo.png" % domain

    def checkalive(self):
        page = self.vods.download(self.domain + "/canli-yayin", referer=self.domain)
        src = re.search("src\:\s?(?:'|\")(.+?)(?:'|\")", page)
        if src:
            self.dataid = "%s|Referer=%s" % (src.group(1), self.domain)
        return self.dataid

    def get(self):
        if not self.dataid:
            self.checkalive()
        yield self.dataid
"""