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
                    chdata = self.download(src, referer=self.channel)
                    regx = "file\s?:\s?(?:'|\")(.+)(?:'|\")"
                    m3u8 = re.search(regx, chdata)
                    if m3u8:
                        m3u8url = m3u8.group(1)
                        headers = {"Referer": src,
                                   "User-Agent": ua}
                        m3u8 = net.tokodiurl(m3u8url, None, headers)
                        yayinlar.append(m3u8)
                    break
        tree = htmlement.fromstring(self.download(self.channel, referer=domain))
        extract(tree)
        for yayin in tree.findall(".//div[@class='alternatif']/.//a"):
            alink = yayin.get("href")
            if alink in linkcache:
                continue
            else:
                linkcache.append(alink)
                extract(htmlement.fromstring(self.download(alink, referer=domain)))

        if len(yayinlar):
            return yayinlar

    def get(self):
        yayinlar = self._check()
        if yayinlar is not None:
            for yayin in yayinlar:
                yield yayin


def create_classes():
    page = net.http(domain, referer=domain)
    mtree = htmlement.fromstring(page)
    """
    trees = [htmlement.fromstring(page)]
    for pg in trees[0].findall(".//div[@class='wp-pagenavi']/a")[:-1]:
        trees.append(htmlement.fromstring(net.http(pg.get("href"), referer=domain)))
    for tree in trees:
    """
    for cat in mtree.findall(".//li[2]/ul[@class='sub-menu']/li/a"):
        tree = htmlement.fromstring(net.http(cat.get("href"), referer=domain))
        for chan in tree.iterfind(".//ul[@class='kanallar']/.//a"):
            cname = chan.get("title")
            url = chan.get("href")
            cid = "channel_%s" % url.replace(":", "").encode("ascii", "replace")
            bdict = {"channel": url,
                     "title": cname,
                     "categories": ["ecanlitv", cat.get("title")]
                     }
            bdict["icon"] = chan.find(".//img").get("src")
            globals()[cid] = type(cid, (ecanli, scraper), bdict)


create_classes()
