# -*- coding: utf-8 -*-

import vods
import re
import htmlement
import json
import uuid
import urllib

from tinyxbmc.tools import elementsrc
from tinyxbmc.net import absurl
from tinyxbmc import const
from tinyxbmc import iso
from tinyxbmc import net
import hashlib


SEARCH_REGEX = r"e\.target\.elements\.s\.value.+?\"(.+?)\""
JS_REGEX = r'script.+?type="text\/javascript" src=\"(.+?)"'
TOKEN_REGEX = r';t="([^,|=]+?)"'
UID = str(uuid.uuid4())


class base:
    page = 1
    useaddonplayers = False

    @property
    def domain(self):
        return "https://%s" % self.setting.getstr("domain")

    @property
    def highq(self):
        return self.setting.getbool("highq")

    @property
    def lastreleased(self):
        return self.setting.getint("lastreleased")

    @property
    def sort(self):
        return self.setting.getstr(f"sort{self.section}")

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
        visitor_info = {'domain': self.setting.getstr("domain"),
                        'uuid': UID,
                        'mouse_moved': True,
                        'suspected_bot': None,
                        'adblock': False}
        cstr = urllib.parse.quote(json.dumps(visitor_info, separators=(',', ':')), safe='{}:')
        cookies = {"visitor_info": cstr}
        pg = net.http(link, referer=referer or self.domain, cookies=cookies, **kwargs)
        if removescr:
            pg = re.sub("<script.*?script>", " ", pg, re.DOTALL)
        if not parse:
            return pg
        return htmlement.fromstring(pg)

    def scrapegrid(self, search=None, filters=None):
        pagenum = self.page or 1
        search_uri = "%s/filter" % self.domain
        query = {"type": self.section,
                 "sort": self.sort,
                 "page": pagenum}
        if self.section == "movie":
            if self.highq:
                query["quality"] = "DVD"
            if self.lastreleased:
                query["released_before"] = self.lastreleased
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
        page = page or self.getpage(link, removescr=True, parse=False)
        imdbid = re.search("(tt[0-9]+)", page)
        if imdbid:
            return imdbid.group(1)

    def scrapeinfo(self, link):
        page = self.getpage(link, removescr=True, parse=True)
        info = {}
        art = {}
        episodes = {}
        imdb = self.scrapeimdb(link)
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
                title = re.sub(r"([a-z])([A-Z])", "\g<1> \g<2>", title)
                episodes[snum].append((epinum, title, url))
        return info, art, episodes

    def itermedias(self, link):
        links = []
        page = self.getpage(link)
        xpage = htmlement.fromstring(page)

        url = None
        for iframe in xpage.iterfind(".//iframe"):
            url = iframe.get("src")
            if url is None:
                continue
            if "primesrc" in url:
                break
        if url is None:
            return

        up = urllib.parse.urlparse(net.absurl(url, link))
        baseurl = f"{up.scheme}://{up.netloc}"
        mediatype = up.path.split("/")[-1]
        params = dict(urllib.parse.parse_qsl(up.query))
        params["type"] = mediatype
        api = net.http(f"{baseurl}/api/v1/s", params=params, json=True)

        for server in api["servers"]:
            sublink = "https://%s/links/go/%s?embed=true" % (self.setting.getstr("domain"), server["key"])
            subpage = self.getpage(sublink, referer=link, json=True)
            media = subpage.get("link")
            if media:
                if media not in links:
                    yield media
                    links.append(media)


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
        if not url:
            return
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
