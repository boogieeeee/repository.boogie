# -*- coding: utf-8 -*-

import vods
import re
import htmlement
import json

from tinyxbmc.tools import elementsrc
from tinyxbmc.net import absurl
from tinyxbmc import const
from tinyxbmc import iso
from tinyxbmc import tools
from tinyxbmc import net
import blowfish
import hashlib
from urllib import parse


SEARCH_REGEX = r"e\.target\.elements\.s\.value.+?\"(.+?)\""
JS_REGEX = r'script.+?type="text\/javascript" src=\"(.+?)"'
TOKEN_REGEX = r';t="([^,|=]+?)"'


class base:
    page = 1
    useaddonplayers = False

    @property
    def domain(self):
        return "https://%s" % self.setting.getstr("domain")

    @property
    def highq(self):
        return self.setting.getbool("highq")

    def getcats(self):
        search_uri = self.domain + "/filter"
        xpage = self.getpage(search_uri, parse=True)
        for genre in xpage.iterfind(".//li[@class='genre-filter-bar']/.//input"):
            genre = genre.get("value")
            if not genre:
                continue
            yield genre.title(), {"genre[]": genre}
        for code, country in iso.countries_2letter.items():
            yield f"Country: {country}", {"country": code.upper()}

    def getpage(self, link, referer=None, parse=False, removescr=False, rel=None, **kwargs):
        if rel is not None:
            link = absurl(link, rel)
        pg = self.download(link, referer=referer or self.domain, **kwargs)
        if removescr:
            pg = re.sub("<script.*?script>", " ", pg, re.DOTALL)
        if not parse:
            return pg
        return htmlement.fromstring(pg)

    def scrapegrid(self, search=None, filters=None):
        pagenum = self.page or 1
        search_uri = "%s/filter" % self.domain
        query = {"type": self.section,
                 "sort": "Trending Today",
                 "page": pagenum}
        if self.highq and self.section == "movie":
            query["quality"] = "DVD"
        if self.page:
            query["page"] = self.page
        if filters:
            query.update(filters)
        if search:
            query["s"] = search
            index_pg = self.getpage(search_uri)
            js_uri = re.search(JS_REGEX, index_pg)
            js_pg = self.getpage(js_uri.group(1), params=query, rel=self.domain)
            search_suffix = re.search(SEARCH_REGEX, js_pg)
            search_hash = hashlib.sha1(((search + search_suffix.group(1))).encode()).hexdigest()[:10]
            query["ds"] = search_hash
        else:
            self.setnextpage(pagenum + 1)
        page = self.getpage(search_uri, parse=True, params=query)
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
                    img = subdiv.find(".//img")
                    art = {}
                    if img is not None:
                        art["icon"] = art["poster"] = art["thumb"] = absurl(img.get("src"), self.domain)
                    info = {}
                    if year:
                        info["year"] = year
                    if self.section == "tv":
                        info["tvshowtitle"] = title
                    elif self.section == "movie":
                        info["title"] = title
                    self.additem(title, url, info, art)

    def scrapeimdb(self, link, page=None):
        page = page or self.getpage(link, removescr=True, parse=True)
        for sublink in page.findall(".//div[@class='movie_info_actions']/div/a"):
            subtext = sublink.text.lower()
            if "imdb" in subtext:
                imdbnumber = re.search("(tt[0-9]+)", sublink.get("href"))
                if imdbnumber:
                    return imdbnumber.group(1)

    def scrapeinfo(self, link):
        page = self.getpage(link, removescr=True, parse=True)
        info = {}
        art = {}
        episodes = {}
        imdb = self.scrapeimdb(link, page)
        if imdb:
            info["imdbnumber"] = imdb

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
                art["icon"] = art["poster"] = art["thumb"] = absurl(img.get("src"), self.domain)

        for season in page.iterfind(".//div[@class='show_season']"):
            snum = int(season.get("data-id"))
            for episode in season.iterfind(".//div"):
                if "tv_episode_item" not in episode.get("class"):
                    continue
                if snum not in episodes:
                    episodes[snum] = []
                a = episode.find(".//a")
                url = absurl(a.get("href"), self.domain)
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
        links = []
        page = self.getpage(link)
        xpage = htmlement.fromstring(page)
        for primesrc in tools.safeiter(self.primesrcv2(page, xpage)):
            if primesrc not in links:
                yield primesrc
                links.append(primesrc)
        for primesrc in tools.safeiter(self.primesrcv1(xpage)):
            if primesrc not in links:
                yield primesrc
                links.append(primesrc)
        src = None
        for js in xpage.iterfind(".//script"):
            src = js.get("src")
            if not src:
                continue
            if src.startswith("/js/app-"):
                break
        jspage = self.getpage(src, rel=self.domain)
        token = re.search(TOKEN_REGEX, jspage).group(1)

        userdata = xpage.find(r".//span[@id='user-data']").get("v")
        codes = blowfish.decrypt(userdata)
        for code in codes:
            sublink = "https://%s/links/go/%s" % (self.setting.getstr("domain"), code)
            try:
                subpage = self.getpage(sublink, json=True, params={"token": token,
                                                                   "emded": "true"})
            except Exception:
                continue
            media = subpage.get("link")
            if media:
                if "streamz.ws" in media:
                    continue
                if media not in links:
                    yield media
                    links.append(media)
                yield media

    def primesrcv1(self, xpage):
        url = None
        for iframe in xpage.iterfind(".//iframe"):
            url = iframe.get("src")
            if url is None:
                continue
            if "primesrc" in url:
                break
        if url is None:
            return

        # v1 api
        up = parse.urlparse(url)
        baseurl = f"{up.scheme}://{up.netloc}"
        mediatype = up.path.split("/")[-1]
        params = dict(parse.parse_qsl(up.query))
        params["type"] = mediatype
        api = net.http(f"{baseurl}/api/v1/s", params=params, json=True)
        for server in api["servers"]:
            api2 = net.http(f"{baseurl}/api/v1/l", params={"key": server["key"]}, json=True)
            yield api2["link"]

    def primesrcv2(self, page, xpage):
        imdb = self.scrapeimdb(None, xpage)
        if not imdb:
            return
        referer = "https://vidsrc.net/"
        if self.section == "tv":
            seasoninfo = re.search(r"episode_info\s*?\=\s*?({.+?\})", page)
            if seasoninfo is None:
                return
            seasoninfo = json.loads(seasoninfo.group(1))
            vidsrcu = f"{referer}embed/{self.section}"
            params = {"imdb": imdb,
                      "season": seasoninfo["season"],
                      "episode": seasoninfo["episode"],
                      "ref": referer}
        else:
            vidsrcu = f"{referer}embed/{self.section}/{imdb}"
            params = {}
        vidsrc = htmlement.fromstring(net.http(vidsrcu, referer=referer, params=params))
        iframe = vidsrc.find(".//iframe")
        if iframe is None:
            return
        iframeu = net.absurl(iframe.get("src"), referer)
        up = parse.urlparse(iframeu)
        serverpath = "/".join(up.path.split("/")[:-1])
        for server in vidsrc.findall(".//div[@class='server']"):
            server = server.get("data-hash")
            serveru = f"{up.scheme}://{up.netloc}{serverpath}/{server}"
            iframesrc = net.http(serveru, referer=vidsrcu)
            iframe2 = re.search(r"src\s*?\:\s*?(?:\"|\')(.+?)(?:\"|\')", iframesrc)
            if iframe2 is None:
                continue
            iframe2u = net.absurl(iframe2.group(1), iframeu)
            iframe2src = net.http(iframe2u, referer=vidsrcu)
            rgxs = [r"location\.replace\((?:\"|\')(.+?)(?:\"|\')",
                    r"btoa\((?:\'|\")(https\:\/\/.+?)(?:\'|\")"]
            for rgx in rgxs:
                iframe3 = re.search(rgx, iframe2src)
                if iframe3 is not None:
                    yield iframe3.group(1)


class pwseries(vods.showextension, base):
    info = {"title": "Primewire Series"}
    section = "tv"
    useaddonplayers = False
    dropboxtoken = const.DB_TOKEN

    def searchshows(self, keyword=None):
        self.scrapegrid(keyword)

    def getshows(self, catargs=None):
        self.scrapegrid(filters=catargs)

    def getcategories(self):
        for catname, filters in self.getcats():
            self.additem(catname, filters)

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

    def getimdb(self, url):
        if not isinstance(url, str):
            return
        return self.scrapeimdb(url)


class pwmovies(vods.movieextension, base):
    info = {"title": "Primewire Movies"}
    section = "movie"
    useaddonplayers = False
    dropboxtoken = const.DB_TOKEN

    def searchmovies(self, keyword=None):
        self.scrapegrid(keyword)

    def getmovies(self, catargs=None):
        self.scrapegrid(filters=catargs)

    def getcategories(self):
        for catname, filters in self.getcats():
            self.additem(catname, filters)

    def geturls(self, link):
        for url in self.itermedias(link):
            yield url

    def getimdb(self, url):
        return self.scrapeimdb(url)
