# -*- coding: utf-8 -*-

import vods
import re
import htmlement
from tinyxbmc.tools import elementsrc
from tinyxbmc.net import absurl
from tinyxbmc import const
import blowfish
import hashlib


SEARCH_REGEX = r"e\.target\.elements\.s\.value.+?\"(.+?)\""
JS_REGEX = r'script.+?type="text\/javascript" src=\"(.+?)"'
TOKEN_REGEX = r';t="(.+?)"'


class base:
    page = 1
    usedirect = False
    useaddonplayers = False

    def scrapegrid(self, search=None, genre=None):
        domain = "https://%s" % self.setting.getstr("domain")
        search_uri = "%s/filter" % domain
        query = {"t": "y", "m": "m", "w": "q", "type": self.section, "sort": "Trending Today"}
        if self.page:
            query["page"] = self.page
        if genre:
            query["genre[]"] = genre
        if search:
            query["s"] = search
            index_pg = self.download(search_uri, referer=domain)
            js_uri = re.search(JS_REGEX, index_pg)
            js_pg = self.download(absurl(js_uri.group(1), domain), params=query, referer=domain)
            search_suffix = re.search(SEARCH_REGEX, js_pg)
            search_hash = hashlib.sha1(((search + search_suffix.group(1))).encode()).hexdigest()[:10]
            query["ds"] = search_hash
        page = htmlement.fromstring(self.download(search_uri, params=query, referer=search_uri))
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
                    url = absurl(subdiv.find(".//a").get("href"), search_uri)
                    info, art, _episodes = self.scrapeinfo(url)
                    if year and not info.get("year"):
                        info["year"] = year
                    if self.section == "tv":
                        info["tvshowtitle"] = title
                    elif self.section == "movie":
                        info["title"] = title
                    self.additem(title, url, info, art)

    def scrapeinfo(self, link):
        domain = "https://%s" % self.setting.getstr("domain")
        pg = self.download(link, referer=domain)
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
                    break

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
            img = infodiv.find(".//img")
            if img is not None:
                art["icon"] = art["poster"] = art["thumb"] = absurl(img.get("src"), domain)

        for season in page.iterfind(".//div[@class='show_season']"):
            snum = int(season.get("data-id"))
            for episode in season.iterfind(".//div"):
                if "tv_episode_item" not in episode.get("class"):
                    continue
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
        xpage = htmlement.fromstring(self.download(link, referer=domain))
        src = None
        for js in xpage.iterfind(".//script"):
            src = js.get("src")
            if not src:
                continue
            if src.startswith("/js/app-"):
                break
        jspage = self.download(absurl(src, domain), referer=domain)
        token = re.search(TOKEN_REGEX, jspage).group(1)
        
        userdata = xpage.find(r".//span[@id='user-data']").get("v")
        codes = blowfish.decrypt(userdata)
        for code in codes:
            sublink = "https://%s/links/go/%s?token=%sembed=true" % (self.setting.getstr("domain"),
                                                                     code,
                                                                     token)
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

    def getseasons(self, url):
        info, art, episodes = self.scrapeinfo(url)
        for snum in sorted(episodes):
            sinfo = info.copy()
            sinfo["season"] = snum
            self.additem("Season %s" % snum, snum, sinfo, art)

    def getepisodes(self, url, snum):
        info, art, episodes = self.scrapeinfo(url)
        for epinum, title, url in episodes.get(snum, []):
            einfo = info.copy()
            einfo["season"] = snum
            einfo["episode"] = epinum
            einfo["title"] = title
            self.additem(title, url, einfo, art)

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

    def geturls(self, link):
        for url in self.itermedias(link):
            yield url
