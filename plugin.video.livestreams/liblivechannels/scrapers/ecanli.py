# -*- encoding: utf-8 -*-
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

from liblivechannels import scraper, scrapers
import re
import htmlement

from tinyxbmc import net

import scrapertools


ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
domain = "https://www.ecanlitvizle.live"

customchannels = {u"CNN Türk": domain + "/cnn-turk-canli",
                  u"Haber Türk": domain + "/haberturk-canli-yayin",
                  u"Show TV": domain + "/show-tv-canli",
                  u"Bloomberg HT": domain + "/bloomberg-ht-canli-yayin",
                  u"Tv 8": domain + "/tv-8-canli-yayin",
                  }


class ecanli_channel(scraper):
    subchannel = True
    tree = None

    def gettree(self):
        if not self.tree:
            self.tree = htmlement.fromstring(self.download(self.channel, referer=domain))

    def _check(self):
        linkcache = [self.channel]

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
                        yield m3u8
                    break

        self.gettree()
        for yayin in extract(self.tree):
            yield yayin
        for yayin in self.tree.findall(".//div[@class='alternatif']/.//a"):
            alink = yayin.get("href")
            if alink in linkcache:
                continue
            else:
                linkcache.append(alink)
                for yayin in extract(htmlement.fromstring(self.download(alink, referer=domain))):
                    yield yayin

    def get(self):
        for yayin in self._check():
            yield yayin
        self.tree = None

    def iterprogrammes(self):
        self.gettree()
        datepsr = scrapertools.dateparser(3)
        pitr = scrapertools.makeprograms(datepsr.datefromhour(0, 0, 0, 1))
        for yayin in self.tree.iterfind(".//ul[@class='yayinakisi']/li/b"):
            hour, minute = yayin.text.strip().split(":")
            date = datepsr.datefromhour(hour, minute)
            yield pitr.add(yayin.tail.strip(), date)
        self.tree = None
        yield pitr.flush()


class ecanli(scrapers):
    def iteratechannels(self):
        page = self.download(domain, referer=domain)
        mtree = htmlement.fromstring(page)
        for cat in mtree.findall(".//li[2]/ul[@class='sub-menu']/li/a"):
            tree = htmlement.fromstring(self.download(cat.get("href"), referer=domain))
            for chan in tree.iterfind(".//ul[@class='kanallar']/.//a"):
                cname = chan.get("title")
                url = chan.get("href")
                iscustom = False
                for customlink in customchannels.values():
                    # the scraped url may have some seo trailing values so check if custom is contained
                    if customlink in url:
                        iscustom = True
                        break
                if iscustom:
                    continue
                subchan = self.makechannel(url, ecanli_channel,
                                           channel=url,
                                           title=cname,
                                           categories=["ecanlitv", cat.get("title")],
                                           icon=chan.find(".//img").get("src"))
                yield subchan

    def getchannel(self, cid, custom=None):
        if custom:
            cid = customchannels.get(custom)
            if not cid:
                return
        tree = htmlement.fromstring(self.download(cid))
        cname = tree.find(".//div[@class='kanaldetay']/h1").text
        categories = ["ecanlitv"]
        icon = tree.find(".//div[@class='kanaldetay']/img").get("src")
        subchan = self.makechannel(cid, ecanli_channel,
                                   channel=cid,
                                   title=cname,
                                   categories=categories,
                                   icon=icon,
                                   tree=tree)
        return subchan


def iterexternal(download, cid):
    ecanli_channel = ecanli(download).getchannel(None, cid)
    if ecanli_channel:
        for media in ecanli_channel(download).get():
            yield media
