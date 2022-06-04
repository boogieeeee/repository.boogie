# -*- coding: utf-8 -*-

import vods
import re
import htmlement
from tinyxbmc.tools import elementsrc
from tinyxbmc.net import absurl
from tinyxbmc import const
import blowfish


class base:
    page = 1
    usedirect = False
    useaddonplayers = False

    def scrapegrid(self, search=None, genre=None):
        domain = "https://%s/filter" % self.setting.getstr("domain")
        query = {"t": "y", "m": "m", "w": "q", "type": self.section, "sort": "Trending"}
        if self.page:
            query["page"] = self.page
        if genre:
            query["genre[]"] = genre
        if search:
            query["s"] = search
        page = htmlement.fromstring(self.download(domain, params=query, referer=domain))
        div = page.find(".//div[@class='index_container']")
        if div is not None:
            for subdiv in div.iterfind(".//div"):
                if subdiv.get("class") and "index_item" in subdiv.get("class"):
                    titlediv = subdiv.find(".//div[@class='title-cutoff']")
                    title = titlediv.text.strip().title()
                    year = elementsrc(subdiv.find("./a/h2"), exclude=titlediv)
                    if year:
                        yearre = re.search("([0-9]{4})", year)
                        if yearre:
                            year = int(yearre.group(1))
                        else:
                            year = None
                    img = subdiv.find(".//img")
                    if img is not None:
                        img = absurl(img.get("src"), domain)
                    else:
                        img = None
                    info = {"title": title, "year": year}
                    if self.section == "tv":
                        info["tvshowtitle"] = title
                    art = {"icon": img, "thumb": img, "poster": img}
                    url = absurl(subdiv.find(".//a").get("href"), domain)
                    self.additem(title, (url, info, art), info, art)

    def scrapeinfo(self, link):
        domain = "https://%s" % self.setting.getstr("domain")
        pg = self.download(link, referer=domain, cache=None)
        pg = re.sub("<script.*?script>", " ", pg, re.DOTALL)
        page = htmlement.fromstringlist(pg)
        info = {}
        art = {}
        episodes = {}
        for sublink in page.findall(".//div[@class='movie_info_actions']/div/a"):
            subtext = sublink.text.lower()
            if "imdb" in subtext:
                imdbnumber = re.search("(tt[0-9]+)", sublink.get("href"))
                if imdbnumber:
                    info["imdbnumber"] = imdbnumber.group(1)
            """
            if "trailer" in subtext:
                info["trailer"] = sublink.get("href")
            """

        infodiv = page.find(".//div[@class='movie_info']")
        if infodiv is not None:
            for tr in infodiv.findall(".//tr")[1:]:
                tds = tr.findall(".//td")
                if not len(tds) == 2:
                    continue
                infotype = elementsrc(tds[0]).strip().lower()
                if "released" in infotype:
                    released = re.search("([0-9]{4})", elementsrc(tds[1]))
                    if released:
                        info["year"] = int(released.group(1))
                if "genre" in infotype:
                    info["genre"] = [elem.text for elem in tds[1].findall(".//a")]
                if "cast" in infotype:
                    info["cast"] = [elem.get("href").split("cast=")[-1].strip().title() for elem in tds[1].findall(".//a")]
                if "runtime" in infotype:
                    runtime = re.search("([0-9]+)\s?min", elementsrc(tds[1]))
                    if runtime:
                        info["duration"] = int(runtime.group(1)) * 60
            img = infodiv.find(".//img")
            if img is not None:
                art["icon"] = art["poster"] = art["thumb"] = absurl(img.get("src"), domain)

        for season in page.iterfind(".//div[@class='show_season']"):
            snum = int(season.get("data-id"))
            for episode in season.iterfind(".//div[@class='tv_episode_item']"):
                if snum not in episodes:
                    episodes[snum] = []
                a = episode.find(".//a")
                url = absurl(a.get("href"), domain)
                epi = a.text
                enum = re.search("([0-9]+)", epi)
                if enum:
                    epinum = int(enum.group(1))
                else:
                    epinum = 0
                title = episode.find(".//span[@class='tv_episode_name']").text.replace("-", "")
                title = re.sub("([a-z])([A-Z])", "\g<1> \g<2>", title)
                episodes[snum].append((epinum, title, url))
        return info, art, episodes

    def itermedias(self, link):
        domain = "https://%s" % self.setting.getstr("domain")
        page = htmlement.fromstring(self.download(link, referer=domain))
        userdata = page.find(".//span[@id='user-data']").get("v")
        codes = blowfish.decrypt(userdata)
        for code in codes:
            sublink = "https://%s/links/go/%s?embed=true" % (self.setting.getstr("domain"), code)
            subpage = self.download(sublink, referer=link, json=True)
            media = subpage.get("link")
            if media:
                if "streamz.ws" in media:
                    continue
                yield media


class pwseries(vods.showextension, base):
    info = {"title": "Primewire Series"}
    section = "tv"
    usedirect = False
    useaddonplayers = False
    dropboxtoken = const.DB_TOKEN

    def searchshows(self, keyword=None):
        self.scrapegrid(keyword)

    def getshows(self, catargs=None):
        self.scrapegrid()

    def getseasons(self, showargs=None):
        url, info, art = showargs
        info2, art2, episodes = self.scrapeinfo(url)
        info.update(info2)
        art.update(art2)
        for snum in sorted(episodes):
            self.additem("Season %s" % snum, (snum, episodes[snum]), info, art)

    def getepisodes(self, showargs=None, seaargs=None):
        _url, info, art = showargs
        snum, episodes = seaargs
        for epinum, title, url in episodes:
            sinfo = info.copy()
            sinfo["season"] = snum
            sinfo["episode"] = epinum
            sinfo["title"] = title
            self.additem(title, url, sinfo, art)

    def geturls(self, link):
        for url in self.itermedias(link):
            yield url


class pwmovies(vods.movieextension, base):
    info = {"title": "Primewire Movies"}
    section = "movie"
    usedirect = False
    useaddonplayers = False
    dropboxtoken = const.DB_TOKEN

    def searchmovies(self, keyword=None):
        self.scrapegrid(keyword)

    def getmovies(self, catargs=None):
        self.scrapegrid()

    def cachemovies(self, args):
        link, _info, _art = args
        info, art, _ = self.scrapeinfo(link)
        return info, art

    def geturls(self, args):
        link, _info, _art = args
        for url in self.itermedias(link):
            yield url
