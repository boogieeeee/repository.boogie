# -*- coding: utf-8 -*-

import re
import vods
import htmlement
from tinyxbmc import const
from tinyxbmc import net


domain = "https://racereplay.net"
regex1 = ".//div[@class='container']/div[@class='row']/div/ul/li"
regex2 = ".//div[@class='container-fluid']/div[@class='row']/div/ul/li"


class replay(vods.showextension):
    info = {"title": "Race Replay"}
    useaddonplayers = False
    loadtimeout = 3
    dropboxtoken = const.DB_TOKEN

    def getcategories(self):
        page = self.download(domain + "/category.php")
        for cat in htmlement.fromstring(page).iterfind(regex2):
            img = cat.find(".//img")
            link = cat.find(".//a")
            if img is not None and link is not None:
                desc = img.get("alt")
                img = img.get("src")
                self.additem(desc, link.get("href"), art={"icon": img,
                                                          "thumb": img,
                                                          "poster": img})

    def getshows(self, catargs=None):
        if not catargs:
            catargs = domain + "/newvideos.php"
        baseurl = self.page or catargs
        page = self.download(baseurl)
        xpage = htmlement.fromstring(page)
        for cat in xpage.iterfind(regex2):
            img = cat.find(".//img")
            link = None
            for a in cat.iterfind(".//a"):
                if a.get("href") is not None and a.get("href").startswith("https://"):
                    link = a.get("href")
                    break
            if img is not None and link is not None:
                desc = img.get("alt")
                img = img.get("src")
                self.additem(desc, link, art={"icon": img,
                                              "thumb": img,
                                              "poster": img})
        for ul in xpage.iterfind(".//div[@class='row']/.//ul"):
            if ul.get("class") is not None and "pagination" in ul.get("class"):
                li = ul.findall(".//li")[-1]
                if li.get("class") is None or "disabled" not in li.get("class"):
                    pagination = li.find(".//a").get("href")
                    if not pagination.startswith("https://"):
                        pagination = domain + "/" + pagination
                    self.setnextpage(pagination)
                    break

    def getepisodes(self, url=None, seaargs=None):
        iframe = htmlement.fromstring(self.download(url)).find(".//iframe").get("src")
        iframesrc = htmlement.fromstring(self.download(iframe, referer=url))
        partlis = iframesrc.findall(".//div[@id='header-slider']/div/ul/li")
        if partlis:
            i = 0
            for li in partlis:
                i += 1
                link = domain + "/F1Part/" + re.search("frame\('(.+?)'", li.get("onclick")).group(1)
                self.additem("Part %d" % i, [link, url])
        else:
            self.additem("Full Event", [iframe, url])

    def geturls(self, args):
        iframe, referer = args
        iframesrc = htmlement.fromstring(self.download(iframe, referer=referer))
        for src in iframesrc.iterfind(".//div[@class='list-servers']/ul/li"):
            link = re.search("loadMovieServer\(\'(.+?)\'", src.get("onclick")).group(1)
            yield link
