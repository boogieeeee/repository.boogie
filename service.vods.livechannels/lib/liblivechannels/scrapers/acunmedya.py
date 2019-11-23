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


class tv8(scraper):
    domain = "https://www.tv8.com.tr"
    m3u8 = None
    title = u"Tv 8"
    icon = "https://img.tv8.com.tr/s/template/v2/img/tv8-logo.png"

    def checkalive(self, group=1):
        url = "%s/canli-yayin" % self.domain
        page = self.vods.download(url, referer=self.domain)
        def checkregex(rgx):
            chk1 = re.search(rgx, page)
            if chk1 is not None:
                return chk1.group(group)

        for rgx in ("push\(\{\'src\'\:\s+\"(.+?)\"", "file\:\s?\"(.+)\""):
            res = checkregex(rgx)
            if res:
                self.m3u8 = res
                break
        return self.m3u8

    def get(self):
        if not self.m3u8:
            self.checkalive()
        yield self.m3u8
