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
import htmlement
import urllib
from tinyxbmc import net

ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
domain = "https://www.ecanlitvizle.live"


class ecanli(object):
    def _check(self):
        linkcache = [self.channel]
        yayinlar = []

        def extract(tree):
            for iframe in tree.findall(".//iframe"):
                src = iframe.get("src")
                if src is not None and "embed.php?" in src:
                    chdata = self.vods.download(src, referer=self.channel)
                    regx = "file\s?:\s?(?:'|\")(.+)(?:'|\")"
                    m3u8 = re.search(regx, chdata)
                    if m3u8 and "etvserver.com/" not in m3u8.group(1):
                        headers = {"Referer": src,
                                   "User-Agent": ua}
                        m3u8 = "%s|%s" % (m3u8.group(1), urllib.urlencode(headers))
                        yayinlar.append(m3u8)
                    break
        tree = htmlement.fromstring(self.vods.download(self.channel, referer=domain))
        extract(tree)
        for yayin in tree.findall(".//div[@class='alternatif']/.//a"):
            alink = yayin.get("href")
            if alink in linkcache:
                continue
            else:
                linkcache.append(alink)
                extract(htmlement.fromstring(self.vods.download(alink, referer=domain)))

        if len(yayinlar):
            return yayinlar

    def get(self):
        yayinlar = self._check()
        if yayinlar is not None:
            for yayin in yayinlar:
                yield yayin


def create_classes():
    cachetime = 60 * 24 * 7
    page = net.http(domain + "/sitemap.xml", referer=domain, cache=cachetime)
    for link in re.finditer("<loc>(.+?)</loc>", page.encode("utf8")):
        url = link.group(1).strip()
        names = re.sub("[0-9]+\/", "/", url).split("/")
        if "/category/" in url:
            continue
        if "-kanallar" in url:
            continue
        if "-channels" in url:
            continue
        if len(names) < 5:
            continue 
        namestrips = ["canli", "kesintisiz", "izle", "hd", "yayin", "film", "series", "live", "stream"]
        cname = names[3].replace("-", " ")
        for namestrip in namestrips:
            cname = cname.replace(namestrip, "")
        cname = cname.replace("  ", " ").title()
        cid = "channel_%s" % url.replace(":", "")
        bdict = {"channel": url,
                 "title": cname,
                 "categories": ["ecanlitv"]
                 }
        logos = list(names)
        logos.insert(3, "logo")
        bdict["icon"] = "/".join(logos[:-1]) + ".png"
        globals()[cid] = type(cid, (ecanli, scraper), bdict)


create_classes()
