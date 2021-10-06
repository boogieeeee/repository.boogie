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
import traceback
import jscrypto
import base64
import binascii

from tinyxbmc import net
from tinyxbmc import tools
from tinyxbmc import gui


domain = "https://www.turkanime.net/"
ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"


class animeturk(vods.showextension):
    usedirect = False
    useaddonplayers = False

    info = {"title": u"Türk Anime TV"
            }
    ismovie = False

    def getpage(self, *args, **kwargs):
        kwargs["timeout"] = 30
        kwargs["http2"] = False
        pg = self.download(*args, **kwargs)
        return pg

    def getcategories(self):
        xpage = htmlement.fromstring(self.getpage("%sajax/turler" % domain,
                                                  headers={"x-requested-with": "XMLHttpRequest"},
                                                  referer=domain))
        for a in xpage.iterfind(".//a"):
            self.additem(a.get("title"), net.absurl(a.get("href"), domain))

    def getshows(self, catargs=None):
        if catargs:
            self.scrapegrid(htmlement.fromstring(self.getpage(catargs)))

    def scrapegrid(self, xpage):
        for div in xpage.iterfind(".//div[@class='panel panel-visible']"):
            a = div.find(".//a[@class='baloon']")
            img = net.absurl(div.find(".//img").get("data-src"), domain)
            art = {"icon": img, "thumb": img, "poster": img}
            title = a.get("title").replace("izle", "").strip()
            url = net.absurl(a.get("href"), domain)
            if "/anime/" in url:
                imgid = re.search("([0-9]+)", img)
                if not imgid:
                    continue
                url = imgid.group(1), art
            self.additem(title, url, art=art)

    def searchshows(self, keyword=None):
        page = self.getpage(domain + "arama", data={"arama": keyword}, method="POST")
        self.scrapegrid(htmlement.fromstring(page))
        if not len(self.items):
            redirect = re.search("window\.location\s*?\=\s*?(?:\"|\')(.+?)(?:\"|\')", page)
            if "anime/" in redirect.group(1):
                url = net.absurl(redirect.group(1), domain)
                page = self.getpage(url, referer=domain)
                xpage = htmlement.fromstring(page)
                div = xpage.find(".//div[@class='table-responsive']/")
                title = div.find(".//tr[2]/td[3]").text
                img = net.absurl(div.find(".//div[@class='imaj']/.//img").get("data-src"), domain)
                imgid = re.search("([0-9]+)", img).group(1)
                art = {"icon": img, "thumb": img, "poster": img}
                url = imgid, art
                self.additem(title, url, art=art)

    def getepisodes(self, showargs=None, seaargs=None):
        if showargs:
            aniid, art = showargs
            url = "%sajax/bolumler&animeId=%s" % (domain, aniid)
            page = self.getpage(url, headers={"x-requested-with": "XMLHttpRequest"})
            for a in htmlement.fromstring(page).iterfind(".//a"):
                href = a.get("href")
                if href and "/video/" in href:
                    title = a.get("title")
                    url = net.absurl(a.get("href"), domain)
                    self.additem(title, url, art=art)
        else:
            self.scrapegrid(htmlement.fromstring(self.getpage(domain)))

    def getlink(self, mirrorlink, xmirrorpage=None):
        try:
            if not xmirrorpage:
                mirrorpage = self.getpage(mirrorlink,
                                          headers={"x-requested-with": "XMLHttpRequest"},
                                          referer=domain)
                xmirrorpage = htmlement.fromstring(mirrorpage)
            iframe = net.absurl(xmirrorpage.find(".//iframe").get("src"), domain)
            iframesrc = self.getpage(iframe,
                                     referer=domain)
            iframe2 = json.loads(re.search("var\s*?iframe\s*?\=\s*?(?:\'|\")(.+)(?:\'|\")", iframesrc).group(1))
            password = re.search("var\s*?pass\s*?\=\s*?(?:\'|\")(.+)(?:\'|\")", iframesrc).group(1)
            link = jscrypto.decrypt(base64.b64decode(iframe2["ct"]),
                                    password,
                                    binascii.unhexlify(iframe2["s"]))
            link = json.loads(link)
            return net.absurl(link, domain)
        except Exception:
            print(traceback.format_exc())

    def iterajaxlink(self, xpage, xpath=None):
        xpath = xpath or ".//button"
        for button in xpage.iterfind(xpath):
            link = button.get("onclick")
            if link:
                ajaxlink = re.search("\((?:\"|\')(ajax.+?)(?:\"|\')", link)
                if ajaxlink:
                    tag = tools.elementsrc(button).encode("ascii", "replace").strip()
                    yield tag, net.absurl(ajaxlink.group(1), domain)

    def geturls(self, id):
        fansubxpath = ".//div[@class='panel-body']/div[1]/button"
        mirrorxpath = ".//div[@class='panel-body']/div[4]/button"

        xpage = htmlement.fromstring(self.getpage(id, referer=domain))

        fansubs = {}

        for fansub, fansublink in tools.safeiter(self.iterajaxlink(xpage, fansubxpath)):
            fansubs[fansub] = fansublink

        if not fansubs:
            for _, mirrorlink in tools.safeiter(self.iterajaxlink(xpage, mirrorxpath)):
                mirror = self.getlink(mirrorlink)
                if mirror:
                    yield mirror
        else:
            fansubselect = gui.select("Select Fansub", list(fansubs.keys()))
            i = -1
            for _fansub, fansublink in fansubs.items():
                i += 1
                if fansubselect == -1 or fansubselect == i:
                    xfansubpage = htmlement.fromstring(self.getpage(fansublink,
                                                                    headers={"x-requested-with": "XMLHttpRequest"},
                                                                    referer=id))
                    mirror = self.getlink(None, xfansubpage)
                    if mirror:
                        yield mirror
                    for _, mirrorlink in tools.safeiter(self.iterajaxlink(xfansubpage, mirrorxpath)):
                        mirror = self.getlink(mirrorlink)
                        if mirror:
                            yield mirror
