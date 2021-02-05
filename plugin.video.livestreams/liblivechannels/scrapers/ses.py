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
from tinyxbmc import tools
from tinyxbmc import net
from scrapertools import yayinakisi
import urlparse
import json
import base64

import htmlement

domain = "https://www.sestv.pw/"

namemap = {"sinema17": "Bein Box Office 1",
           "sinema16": "Dizi TV",
           "sinema15": "Sinema TV 1001",
           "sinema14": "Sinema TV Aksiyon",
           "sinema13": "Sinema TV Aile",
           "sinema19": u"Bein Movies Turk",
           "nickeledeon": "Nickelodeon"
           }


class ses_chan(scraper):
    subchannel = True
    categories = ["ses"]

    def get(self):
        up = urlparse.urlparse(self.url)
        chid = up.path.split("/")[-1]
        subpage = htmlement.fromstring(self.download(self.url, referer=domain))
        embedlink = subpage.find(".//iframe").get("src")
        embedpage = htmlement.fromstring(self.download(embedlink, referer=self.url))
        script = embedpage.find(".//script[@id='v']")
        jsurl = "%s://%s/embed/%s" % (up.scheme, up.netloc, chid)
        data = {"e": 1, "id": script.get("data-i")}
        scode = self.download(jsurl, referer=embedlink,
                              data=data, headers={"x-requested-with": "XMLHttpRequest"},
                              method="POST")
        url = None
        for suffix in ["", "=", "=="]:
            try:
                url = base64.b64decode(scode[::-1] + suffix)
            except Exception:
                continue
        if url:
            yield net.tokodiurl(url, headers={"referer": domain})

    def iterprogrammes(self):
        for prog in yayinakisi.iterprogramme(self.title):
            yield prog


class ses(scrapers):
    def iterpage(self, xpage):
        for a in xpage.iterfind(".//div[@class='content container']/div/div/ul/li/a"):
            href = net.absurl(a.get("href").split("#")[0], domain)
            chname = tools.elementsrc(a).lower().strip()
            if "xxx" in chname.lower():
                continue
            normname = yayinakisi.normalize(chname)
            if normname in namemap:
                chname = namemap[normname]
            icon = a.find(".//img")
            if icon is not None:
                icon = net.absurl(icon.get("src"), domain)
            meta = json.dumps([href, chname, icon])
            yield self.makechannel(meta, ses_chan, url=href, title=chname, icon=icon)

    def iteratechannels(self):
        xpage = htmlement.fromstring(self.download(domain))
        for ch in self.iterpage(xpage):
            yield ch
        pagination = xpage.findall(".//ul[@id='sayfalama']/.//a")
        lastpage = pagination[-1].get("href").split("/")[-1]
        for i in range(2, int(lastpage) + 1):
            xpage = htmlement.fromstring(self.download(domain + "/p/%s" % i))
            for ch in self.iterpage(xpage):
                yield ch

    def getchannel(self, cid):
        url, chname, icon = json.loads(cid)
        return self.makechannel(cid, ses_chan, url=url, title=chname, icon=icon)
