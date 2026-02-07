# -*- coding: utf-8 -*-
import vods
from tinyxbmc import const
from tinyxbmc import net
from tinyxbmc import addon
from tinyxbmc import mediaurl
from tinyxbmc import tools
import htmlement

from urllib import parse


setting = addon.kodisetting("service.vods.livetv")
domain = "https://" + setting.getstr("domain")


class livetv(vods.showextension):
    dropboxtoken = const.DB_TOKEN

    info = {"title": "LiveTV"}

    def getcategories(self):
        page = net.http(domain + "/enx/allupcomingsports/1", verify=False)
        xpage = htmlement.fromstring(page)
        cats = {}
        for a in xpage.iterfind(".//a[@class='main']"):
            img = a.find(".//img")
            url = net.absurl(a.get("href"), domain)
            if img is None and url in cats:
                self.additem(tools.elementsrc(a), url, None, {"thumb": cats[url]})
            else:
                cats[url] = net.absurl(img.get("src"), domain)

    def getshows(self, cat=None):
        cat = cat or domain + "/enx/allupcoming"
        page = net.http(cat, verify=False)
        xpage = htmlement.fromstring(page)
        others = []
        urls = []
        for table in xpage.iterfind(".//table[@class='main']/.//a[@class='live']......"):
            a = table.find(".//a[@class='live']")
            if a is None:
                continue
            title = tools.elementsrc(a)
            url = net.absurl(a.get("href"), domain)
            if url in urls:
                continue
            urls.append(url)
            art = {}
            icon = table.find(".//td[1]/img")
            if icon is not None:
                icon = net.absurl(icon.get("src"), domain)
                art["thumb"] = icon
            liveimg = table.find(".//td[2]/img")
            if liveimg is not None and "live." in liveimg.get("src"):
                title = "[LIVE] " + title
                self.additem(title, url, None, art)
            else:
                others.append([title, url, None, art])
        for other in others:
            self.additem(*other)

    def geturls(self, url):
        if isinstance(url, mediaurl.BaseUrl):
            yield url
            return
        page = net.http(url, verify=False)
        xpage = htmlement.fromstring(page)
        iframe = xpage.find(".//td[@align='center']/.//iframe")
        if iframe is not None:
            iframe = iframe.get("src")
            for rep in ["\r", "\n"]:
                iframe = iframe.replace(rep, "")
            yield net.tokodiurl(net.absurl(iframe, url), headers={"referer": url})

    def getepisodes(self, showargs=None, seaargs=None):
        page = net.http(showargs, verify=False)
        xpage = htmlement.fromstring(page)
        aces = []
        webs = []
        for table in xpage.iterfind(".//table[@class='lnktbj']"):
            img = table.find(".//td[1]/img")
            lang = img.get("title")
            img = net.absurl(img.get("src"), domain)
            bitrate = table.find(".//td[@class='bitrate']")
            if bitrate is None:
                bitrate = ""
            else:
                bitrate = tools.elementsrc(bitrate)
            link = table.find(".//td[7]/a")
            if link is None:
                link = table.find(".//td[6]/a")
            link = link.get("href")
            if link.startswith("acestream://"):
                aces.append([lang, "acestream", bitrate, img, mediaurl.AceUrl(link)])
            else:
                link = net.absurl(link, domain)
                source = dict(parse.parse_qsl(parse.urlparse(link).query)).get("t", "web")
                if source == "ifr":
                    source = "web"
                webs.append([lang, source, bitrate, img, link])

        for results in [aces, webs]:
            results.sort(key=lambda x: (x[0], x[1]))
            for lang, source, bitrate, img, link in results:
                title = f"{lang} {source} {bitrate}"
                self.additem(title, link, None, art={"thumb": img})
