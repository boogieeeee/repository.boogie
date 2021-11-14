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
import json

from six.moves.urllib import parse
from tinyxbmc.const import DB_TOKEN


class webteizle(vods.movieextension):
    dropboxtoken = DB_TOKEN
    usedirect = False
    useaddonplayers = False

    info = {"title": "Webteizle"
            }

    def init(self):
        self._domain = self.setting.getstr("domain")
        self.domain = "https://%s" % self._domain
        self.encoding = "iso-8859-9"

    def gettree(self, url):
        if url is None:
            url = ""
        return htmlement.fromstring(self.download(self.domain + url, encoding=self.encoding, referer=self.domain))

    def getcategories(self):
        for div in self.gettree("/filtre.asp").iterfind(".//div[@class='field'][3]/.//div[@class='item']"):
            cat = div.get("data-value")
            self.additem(cat, "/filtre.asp?a=&ulke=&tur=%s&yayinlanan=2&minYil=&maxYil=&minImdb=&siralama_tipi=3&siralama_turu=desc&ps=60&uyeliste=0" % parse.quote(cat.encode("utf8")))

    def getmovies(self, cat=None):
        tree = self.gettree(cat)
        for div in tree.iterfind(".//div[@id='sol']/div/div"):
            title = div.find(".//div[@class='filmname']")
            if title is not None:
                img = div.find(".//img")
                imgsrc = "https:" + img.get("data-src")
                filmid = re.search("\/a([0-9]+?)\.jpg", imgsrc)
                href = div.find(".//a").get("href")
                info = {"tvshowtitle": title.text}
                year = div.find(".//span[@class='year']").text
                if year is not None and year.isdigit():
                    info["year"] = int(year)
                art = {"icon": imgsrc, "thumb": imgsrc, "poster": imgsrc}
                if filmid is not None:
                    filmid = filmid.group(1)
                args = filmid, href
                self.additem(title.text, args, info, art)

    def searchmovies(self, keyword):
        url = self.domain + "/ajax/arama.asp"
        results = self.download(url, referer=self.domain + "/", data={"q": keyword},
                                method="POST", json=True,
                                headers={"x-requested-with": "XMLHttpRequest"})
        for movie in results.get("results", {}).get("filmler", {}).get("results", []):
            title = movie["title"]
            img = self.domain + movie["image"]
            info = {"tvshowtitle": title}
            art = {"icon": img, "thumb": img, "poster": img}
            filmid = re.search("\/a([0-9]+?)\.jpg", img).group(1)
            args = filmid, self.domain + movie["url"]
            self.additem(title, args, info, art)

    def geturls(self, args):
        bid, url = args
        if not bid:
            tree = self.gettree(url)
            bid = tree.find(".//a[@id='wip']").get("data-id")
        url = self.domain + url
        for dil in range(2):
            data = {"filmid": bid, "dil": dil, "s": "", "b": ""}
            jsdata = self.download(self.domain + "/ajax/dataAlternatif3.asp",
                                   data=data,
                                   referer=url,
                                   method="POST",
                                   encoding=self.encoding,
                                   headers={"x-requested-with": "XMLHttpRequest"})
            js = json.loads(jsdata)
            if js.get("status") == "success":
                for data in js["data"]:
                    iframe = self.download(self.domain + "/ajax/dataEmbed.asp",
                                           data={"id": data["id"]},
                                           referer=url,
                                           encoding=self.encoding,
                                           method="POST")
                    v_url = self.videourl(iframe)
                    if v_url:
                        yield v_url

    def videourl(self, iframe):
        v_id = re.search("\<script\>(.+?)\((?:\"|')(.+?)(?:\"|')\s*?\,\s*?(?:\"|')(.+?)(?:\"|')\)", iframe, re.IGNORECASE)
        if v_id:
            v_server = v_id.group(1).lower()
            v_sid = v_id.group(2)[2:-2]
            if v_server == "vidmoly":
                return "https://vidmoly.to/embed-%s.html" % v_sid
            elif v_server == "netu":
                return "https://yandexcdn.com/player/embed_player.php?vid=%s&autoplay=no" % v_sid
            elif v_server == "mailru":
                v_sid = v_sid.replace("/_myvideo/", "/video/embed/_myvideo/")
                return "https://my.mail.ru/%s?autoplay=1" % v_sid
            elif v_server == "uptobox":
                return "https://uptostream.com/iframe/%s" % v_sid
            elif v_server == "okru":
                return "https://odnoklassniki.ru/videoembed/%s" % v_sid
            elif v_server == "fembed":
                return "https://fembed.com/v/%s" % v_sid
            elif v_server == "streamsb":
                return "https://streamsb.net/play/%s" % v_sid
            elif v_server == "userload":
                return "https://userload.co/embed/%s" % v_sid
            else:
                return iframe
