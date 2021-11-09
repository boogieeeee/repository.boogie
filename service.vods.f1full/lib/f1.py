# -*- coding: utf-8 -*-

import vods
import htmlement
import re
from tinyxbmc import net
from chromium import Browser


domain = "https://f1fullraces.com"


class full(vods.showextension):
    info = {"title": "f1 Full Races"}
    usedirect = False
    useaddonplayers = False
    loadtimeout = 1

    def getcategories(self):
        pass
        with Browser(loadtimeout=self.loadtimeout) as browser:
            page = browser.navigate(self.page or domain)

        xpath = ".//ul[@id='menu-menu-1']/li/ul[@class='sub-menu']/li/ul[@class='sub-menu']/li/a"

        for a in htmlement.fromstring(page).iterfind(xpath):
            self.additem(a.text, a.get("href"))

    def getshows(self, catargs=None):
        with Browser(loadtimeout=self.loadtimeout) as browser:
            page = browser.navigate(self.page or catargs or domain)
        xpage = htmlement.fromstring(page)
        for div in xpage.iterfind(".//div[@class='masonry-inner']"):
            a = div.find(".//h2/a")
            self.additem(a.text, a.get("href"))
        nextp = xpage.find(".//li[@class='next right']/a")
        if nextp is not None:
            self.setnextpage(nextp.get("href"), "Next")

    def getepisodes(self, showargs=None, seaargs=None):
        with Browser(loadtimeout=self.loadtimeout) as browser:
            page = browser.navigate(showargs)
        links = {}
        center = re.search("\<center\>(.+?)\<\/center\>", page, re.DOTALL)
        regexes = ["(.+?)\n[\t\s]*?\<iframe.+src=\"(.+?)\"",
                   "(.+?)\n[\t\s]*?\<a.+href=\"(.+?)\""]
        for rgx in regexes:
            for part, link in re.findall(rgx, center.group(1)):
                part = re.sub("<.*?>", "", part).strip()
                if part not in links:
                    links[part] = []
                link = net.absurl(link, domain)
                if link not in links[part]:
                    links[part].append(link)
        for part, link in links.items():
            self.additem(part, link)

    def geturls(self, urls):
        for url in urls:
            yield url
