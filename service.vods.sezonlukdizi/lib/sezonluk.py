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
from six.moves.urllib import parse

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
        resp = self.download(net.absurl(url, self.domain), encoding=self.encoding, referer=self.domain, text=False)
        domain = parse.urlparse(resp.url).netloc
        if not domain == self._domain:
            self.setting.set("domain", domain)
            self.init()
        return htmlement.fromstring(resp.content.decode(self.encoding))

    def getcategories(self):
        for div in self.gettree("").iterfind(".//div"):
            dcls = div.get("class")
            if dcls is not None and "turler" in dcls:
                for a in div.iterfind(".//a[@class='item']"):
                    self.additem(a.text, a.get("href"))
                break

    def getshows(self, cat=None):
        if cat:
            pagenum = self.page or 1
            cat = f"{cat}&s={pagenum}"
            for a in self.gettree(cat).iterfind(".//a[@class='column']"):
                title = a.find(".//div[@class='description']").text
                img = self.domain + a.find(".//img").get("data-src")
                info = {"tvshowtitle": title}
                art = {"icon": img, "thumb": img, "poster": img}
                href = a.get("href")
                self.additem(title, href.replace("/diziler/", "/bolumler/"), info, art)
            self.setnextpage(pagenum + 1)

    def searchshows(self, keyword):
        # FIXME: this is only giving top results but not all
        url = self.domain + "/ajax/arama.asp"
        results = self.download(url, referer=self.domain + "/", data={"q": keyword},
                                method="POST", json=True,
                                headers={"x-requested-with": "XMLHttpRequest"},
                                cache=None,
                                stream=False)
        for dizi in results.get("results", {}).get("diziler", {}).get("results", []):
            title = dizi["title"]
            img = None
            if dizi.get("image"):
                img = self.domain + dizi["image"]
            info = {"tvshowtitle": title}
            art = {"icon": img, "thumb": img, "poster": img}
            self.additem(title, dizi["url"].replace("/diziler/", "/bolumler/"), info, art)

    def getseasons(self, url):
        tree = self.gettree(url)
        for a in tree.iterfind(".//div[@class='two wide column']/.//a"):
            season = int(a.get("data-tab").strip())
            s_info = {"season": season}
            self.additem("Season %s" % season, [url, season], s_info)

    def getepisodes(self, link=None, seasonargs=None):
        if not link:
            pagenum = self.page or 1
            url = f"{self.domain}/ajax/dataDefaultSonCikan.asp?d=-1&k=0&s={pagenum}"
            page = self.download(url, referer=self.domain + "/",
                                 method="POST",
                                 headers={"x-requested-with": "XMLHttpRequest"},
                                 encoding=self.encoding)
            tree = htmlement.fromstring(page)
            for a in tree.iterfind(".//div[@class='content']/a"):
                img = a.find(".//img")
                imgsrc = self.domain + img.get("src")
                href = a.get("href")
                ss = re.search(r"(.+?)\s([0-9]+)\.Sezon ([0-9]+)\.Bölüm", img.get("alt"))
                title = ss.group(1).strip()
                season = int(ss.group(2))
                epi = int(ss.group(3))
                info = {"tvshowtitle": title, "season": season, "episode": epi}
                serieurl = "/diziler" + "/".join(href.split("/")[:-1])
                art = {"icon": imgsrc, "thumb": imgsrc, "poster": imgsrc}
                args = [serieurl, href]
                self.additem("%s S%sE%s" % (title, season, epi), args, info, art)
            self.setnextpage(pagenum + 1)
        if seasonargs:
            url, season = seasonargs
            seanum = int(season)
            tree = self.gettree(url)
            info = {"season": seanum}
            for tr in tree.iterfind(".//div[@data-tab='%s']/.//tr" % seanum):
                tds = tr.findall(".//td")
                if len(tds) > 3:
                    e_val = tds[2].find(".//a").text
                    e_val = re.search(r"([0-9]+)", e_val)
                    if e_val:
                        e_val = int(e_val.group(1))
                        epilink = tds[3].find(".//a")
                        e_info = info.copy()
                        e_info["title"] = epilink.text
                        e_info["episode"] = e_val
                        args = [url, epilink.get("href")]
                        self.additem("S%sE%s: %s" % (seanum, e_val, epilink.text), args, e_info)

    def getimdb(self, url):
        if isinstance(url, list):
            # for cat args
            url = url[0]
        tree = self.gettree(url)
        for link in tree.iterfind(".//div[@class='right menu']/.//a"):
            href = link.get("href")
            if not href:
                continue
            imdb = re.search(r"\/(tt[0-9]+)", href)
            if not imdb:
                continue
            return imdb.group(1)

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
            undesireds = ["rubyvid"]
            lowprios = []
            js = self.download(self.domain + "/ajax/dataAlternatif22.asp",
                               data=data,
                               referer=self.domain + url,
                               json=True,
                               method="POST",
                               headers={"x-requested-with": "XMLHttpRequest"},
                               cache=None)
            if js.get("status") == "success":
                for data in js["data"]:
                    iframe = self.download(self.domain + "/ajax/dataEmbed22.asp",
                                           data={"id": data["id"]},
                                           referer=self.domain + url,
                                           encoding=self.encoding,
                                           method="POST",
                                           headers={"x-requested-with": "XMLHttpRequest"},
                                           cache=None)
                    v_url = re.search(r"src\s*?\=\s*?(?:\"|')(.+?)(?:\"|')", iframe, re.IGNORECASE)
                    if v_url:
                        v_url = v_url.group(1)
                        if v_url.startswith("//"):
                            v_url = "https:" + v_url
                        media = net.tokodiurl(v_url, headers={"Referer": self.domain})
                        for undesired in undesireds:
                            if undesired in v_url:
                                lowprios.append(media)
                                break
                        if media not in lowprios:
                            yield media
            for lowprio in lowprios:
                yield lowprio
                        
