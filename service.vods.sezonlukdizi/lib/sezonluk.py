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

from tinyxbmc import const
from tinyxbmc import net
from tinyxbmc import tools
from tinyxbmc import gui


class dizi(vods.showextension):
    dropboxtoken = const.DB_TOKEN
    usedirect = False
    useaddonplayers = False

    info = {"title": "Sezonluk Dizi"
            }
    ismovie = False

    def init(self):
        self._domain = self.setting.getstr("domain")
        self.domain = "https://%s" % self._domain
        self.encoding = "iso-8859-9"

    def gettree(self, url):
        return htmlement.fromstring(self.download(net.absurl(url, self.domain), encoding=self.encoding, referer=self.domain))

    def getcategories(self):
        for div in self.gettree("").iterfind(".//div"):
            dcls = div.get("class")
            if dcls is not None and "turler" in dcls:
                for a in div.iterfind(".//a[@class='item']"):
                    self.additem(a.text, a.get("href"))
                break

    def getshows(self, cat=None):
        if cat:
            for a in self.gettree(cat).iterfind(".//a[@class='column']"):
                title = a.find(".//div[@class='description']").text
                img = self.domain + a.find(".//img").get("data-src")
                info = {"tvshowtitle": title}
                art = {"icon": img, "thumb": img, "poster": img}
                self.additem(title, (info, art, a.get("href").replace("/diziler/", "/bolumler/")), info, art)

    def searchshows(self, keyword):
        url = self.domain + "/ajax/arama.asp"
        results = self.download(url, referer=self.domain + "/", data={"q": keyword},
                                method="POST", json=True,
                                headers={"x-requested-with": "XMLHttpRequest"})
        for dizi in results.get("results", {}).get("diziler", {}).get("results", []):
            title = dizi["title"]
            img = None
            if dizi.get("image"):
                img = self.domain + dizi["image"]
            info = {"tvshowtitle": title}
            art = {"icon": img, "thumb": img, "poster": img}
            self.additem(title, (info, art, dizi["url"].replace("/diziler/", "/bolumler/")), info, art)

    def getseasons(self, showargs=None):
        if showargs:
            info, art, url = showargs
            for a in self.gettree(url).iterfind(".//div[@class='two wide column']/.//a"):
                self.additem("Season %s" % a.get("data-tab"), a.get("data-tab"), info, art)

    def getepisodes(self, showargs=None, seaargs=None):
        if not showargs:
            tree = self.gettree("")
            for a in tree.iterfind(".//div[@class='content']/a"):
                img = a.find(".//img")
                imgsrc = self.domain + img.get("src")
                href = a.get("href")
                ss = re.search(u"(.+?)\s([0-9]+)\.Sezon ([0-9]+)\.Bölüm", img.get("alt"))
                title = ss.group(1)
                season = int(ss.group(2))
                epi = int(ss.group(3))
                info = {"tvshowtitle": title, "season": season, "episode": epi}
                art = {"icon": imgsrc, "thumb": imgsrc, "poster": imgsrc}
                args = (None, href)
                self.additem("%s S%sE%s" % (title, season, epi), args, info, art)
        if seaargs:
            info, art, url = showargs
            seanum = int(seaargs)
            for tr in self.gettree(url).iterfind(".//div[@data-tab='%s']/.//tr" % seanum):
                tds = tr.findall(".//td")
                if len(tds) > 3:
                    i = tds[0].find(".//i")
                    if i is None:
                        continue
                    bid = i.get("bid")
                    e_val = tds[2].find(".//a").text
                    e_val = re.search("([0-9]+)", e_val)
                    if e_val:
                        e_val = int(e_val.group(1))
                        epilink = tds[3].find(".//a")
                        e_info = info.copy()
                        e_info["title"] = epilink.text
                        e_info["episode"] = e_val
                        e_info["season"] = seanum
                        args = (bid, self.domain + epilink.get("href"))
                        self.additem("S%sE%s: %s" % (seanum, e_val, epilink.text), args, info, art)

    def geturls(self, args):
        _, url = args
        tree = self.gettree(url)
        bid = tree.find(".//div[@id='dilsec']").get("data-id")
        diller = dict([(tools.elementsrc(x).strip(), x.get("data-dil")) for x in tree.findall(".//div[@id='dilsec']/a")])
        dilkeys = list(diller.keys())
        dil = gui.select("Choose Language", dilkeys)
        if dil == -1:
            dilmap = diller.values()
        else:
            dilmap = [diller[dilkeys[dil]]]
        for dil in dilmap:
            data = {"bid": bid, "dil": dil}
            js = self.download(self.domain + "/ajax/dataAlternatif2.asp",
                               data=data,
                               referer=url,
                               json=True,
                               method="POST",
                               headers={"x-requested-with": "XMLHttpRequest"})
            if js.get("status") == "success":
                for data in js["data"]:
                    iframe = self.download(self.domain + "/ajax/dataEmbed.asp",
                                           data={"id": data["id"]},
                                           referer=url,
                                           encoding=self.encoding,
                                           method="POST")
                    v_url = re.search("src\s*?\=\s*?(?:\"|')(.+?)(?:\"|')", iframe, re.IGNORECASE)
                    if v_url:
                        v_url = v_url.group(1)
                        if v_url.startswith("/player/"):
                            subpage = self.download(self.domain + v_url, referer=url, encoding=self.encoding)
                            iframe = re.search("iframe.+?src\s*?\=\s*?(?:\"|')(.+?)(?:\"|')", subpage)
                            if iframe:
                                v_url = iframe.group(1)
                            else:
                                continue
                        if v_url.startswith("//"):
                            v_url = "https:" + v_url
                        yield v_url
