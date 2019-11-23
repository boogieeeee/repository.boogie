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
import vods
import htmlement
import re


class piabet(vods.movieextension):
    uselinkplayers = False
    useaddonplayers = False

    def getdomain(self):
        domain = self.setting.getstr("domain")
        if not domain.startswith("http"):
            domain = "https://" + domain
        if domain.endswith("/"):
            domain = domain[:-1]
        return domain

    def getmovies(self, args=None):
        page = self.download(self.getdomain())
        tree = htmlement.fromstring(page)
        for channel in tree.findall(".//div/div"):
            cls = channel.get("class")
            if cls and cls.startswith("item"):
                prefix = "[%s] " % cls.replace("item", "").replace("active", "").strip().title()
                url = channel.find(".//a")
                title = channel.find(".//strong")
                tm = channel.find(".//span[@class='time']")
                lv = channel.find(".//span[@class='live']")
                if lv is not None:
                    prefix += "[LIVE] "
                if tm is not None:
                    prefix += "%s " % tm.text
                if title is not None and url is not None:
                    self.additem(prefix + title.text, url.get("href"))

    def geturls(self, url):
        cpage = self.download(url, referer=self.getdomain())
        tree = htmlement.fromstring(cpage)
        for iframe in tree.findall(".//iframe"):
            src = iframe.get("src")
            if "/channel/watch" in src:
                ipage = self.download(src, referer=url)
                b64 = re.search(r'eval\(atob\("(.+?)"\)\)', ipage)
                if b64:
                    code = b64.group(1).decode("base64")
                    for source in re.findall('source:"(.+?)"', code):
                        if ".m3u8" in source:
                            m3u8 = "%s|Referer=%s" % (source, src)
                            yield m3u8
                            break
                break
