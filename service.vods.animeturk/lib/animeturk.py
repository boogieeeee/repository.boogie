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
import html
from urllib import parse

from tinyxbmc import net
from tinyxbmc import tools
from tinyxbmc import gui
from tinyxbmc import const


domain = "https://www.turkanime.tv"


class animeturk(vods.showextension):
    useaddonplayers = False
    dropboxtoken = const.DB_TOKEN

    info = {"title": u"Türk Anime TV"
            }
    ismovie = False

    def init(self):
        self.masterkey = self.setting.getstr("masterkey").encode()

    def iterkeys(self):
        yield self.masterkey
        page = net.http(domain + "/embed/", referer=domain)
        for js in re.findall('"(\/embed\/js.*?)"', page):
            jspage = net.http(domain + js, referer=domain)
            # find sub jspages
            if jspage is None:
                continue
            for subjs in re.findall('([a-f0-9]{8,})', jspage):
                subjspage = net.http(domain + "/embed/js/embeds." + subjs + ".js", referer=domain)
                if subjspage is None:
                    continue
                # find stringlist
                for stringlist in re.findall("var _0x[a-z0-9]+?=\[(.*?)\];", subjspage):
                    # search for strings greater than 64 chars length (normally 100)
                    for keycandidate in re.findall("'([^\']{64,})'", stringlist):
                        yield html.unescape(keycandidate).encode()

    def decrypt(self, data, iv, salt):
        for password in self.iterkeys():
            try:
                retval = jscrypto.decrypt(data, password, iv, salt)
                retval = json.loads(retval)
                if not password == self.masterkey:
                    print("master key updated: %s" % password)
                    self.setting.set("masterkey", password.decode())
                    self.masterkey = password
                return retval
            except Exception:
                print("key failed: %s" % password)
                print(traceback.format_exc())

    def getcategories(self):
        u = "%s/ajax/turler" % domain
        page = net.http(u, referer=domain, headers={"x-requested-with": "XMLHttpRequest"})
        # page = self.download(u, headers=headers, referer=domain)
        xpage = htmlement.fromstring(page)
        for a in xpage.iterfind(".//a"):
            self.additem(a.get("title"), net.absurl(a.get("href"), domain))

    def getshows(self, catargs=None):
        if catargs:
            page = net.http(catargs, referer=domain)
            self.scrapegrid(htmlement.fromstring(page))

    def scrapegrid(self, xpage):
        for div in xpage.iterfind(".//div[@class='panel panel-visible']"):
            a = div.find(".//a[@class='baloon']")
            img = div.find(".//img").get("data-src")
            if not img:
                img = div.find(".//img").get("src")
            img = net.absurl(img, domain)
            art = {"icon": img, "thumb": img, "poster": img}
            for attr in ["title", "data-original-title"]:
                title = a.get(attr)
                if title:
                    break
            title = title.replace("izle", "").strip()
            url = net.absurl(a.get("href"), domain)
            if "/anime/" in url:
                imgid = re.search("([0-9]+)", img)
                if not imgid:
                    continue
                url = imgid.group(1), art
            self.additem(title, url, art=art)

    def searchshows(self, keyword=None):
        # get the forntpage just in case cloudflare kicks in
        _page = net.http(domain)
        page = net.http(domain + "/arama", data={"arama": keyword}, referer=domain, method="POST", cache=None)
        self.scrapegrid(htmlement.fromstring(page))
        if not len(self.items):
            redirect = re.search("window\.location\s*?\=\s*?(?:\"|\')(.+?)(?:\"|\')", page)
            if redirect and "anime/" in redirect.group(1):
                url = net.absurl(redirect.group(1), domain)
                page = net.http(url, referer=domain)
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
            url = "%s/ajax/bolumler&animeId=%s" % (domain, aniid)
            page = net.http(url, referer=domain, headers={"x-requested-with": "XMLHttpRequest"})
            for a in htmlement.fromstring(page).iterfind(".//a"):
                href = a.get("href")
                if href and "/video/" in href:
                    title = a.get("title")
                    url = net.absurl(a.get("href"), domain)
                    self.additem(title, url, art=art)
        else:
            self.scrapegrid(htmlement.fromstring(net.http(domain)))

    def getlink(self, mirrorlink, xmirrorpage=None):
        if not xmirrorpage:
            mirrorpage = net.http(mirrorlink,
                                  referer=domain,
                                  headers={"x-requested-with": "XMLHttpRequest"})
            xmirrorpage = htmlement.fromstring(mirrorpage)
        iframe = net.absurl(xmirrorpage.find(".//iframe").get("src"), domain)
        urldata = parse.urlparse(iframe).fragment.split("/")[2].split("?")[0]
        urldata = json.loads(base64.b64decode(urldata))
        link = self.decrypt(base64.b64decode(urldata["ct"]),
                            binascii.unhexlify(urldata["iv"]),
                            binascii.unhexlify(urldata["s"]))
        return net.absurl(link, domain)

    def iterajaxlink(self, xpage, xpath=None):
        xpath = xpath or ".//button"
        for button in xpage.iterfind(xpath):
            link = button.get("onclick")
            if link:
                ajaxlink = re.search("\((?:\"|\')(ajax.+?)(?:\"|\')", link)
                if ajaxlink:
                    tag = tools.elementsrc(button).encode("ascii", "replace").strip()
                    yield tag, net.absurl(ajaxlink.group(1), domain)

    def geturls(self, uid):
        fansubxpath = ".//div[@class='panel-body']/div[1]/button"
        mirrorxpath = ".//div[@class='panel-body']/div[4]/button"

        page = net.http(uid, referer=domain)
        xpage = htmlement.fromstring(page)

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
                    page = net.http(fansublink, referer=uid, headers={"x-requested-with": "XMLHttpRequest"})
                    xfansubpage = htmlement.fromstring(page)
                    mirror = self.getlink(None, xfansubpage)
                    if mirror:
                        yield mirror
                    for _, mirrorlink in tools.safeiter(self.iterajaxlink(xfansubpage, mirrorxpath)):
                        mirror = self.getlink(mirrorlink)
                        if mirror:
                            yield mirror
