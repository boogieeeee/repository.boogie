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

import re
import json
import time
import urllib
import string
import urlparse
from operator import itemgetter

import htmlement
from tinyxbmc.net import __cookie as cj


searchstr = "evokjaqbb3"
setstr = "huHjVNHSGKomdiqHBMiBpCQYK"
slkstr = "0A6ru35y"
slk = slkstr + "yi5yn4THYpJqy0X82tE95btV"


def iframe(src):
    ret = None
    for sep in ['"', "'"]:
        res = re.findall("<iframe*.?src=" + sep + "(.*?)" + sep, src, re.IGNORECASE)
        if len(res):
            ret = res[0]
            break
    if not ret:
        res = re.findall('window.open\(\"(.*?)\"\)', src)
        if len(res):
            ret = res[0]
    return ret


def caesar(plaintext, shift):
    lower = string.ascii_lowercase
    lower_trans = lower[shift:] + lower[:shift]
    alphabet = lower + lower.upper()
    shifted = lower_trans + lower_trans.upper()
    return plaintext.translate(string.maketrans(alphabet, shifted))


def srapegrid(self, cat=None):
    domain = "https://%s" % self.setting.getstr("domain")
    if self.page:
        n = self.page
    else:
        n = 1
    if not cat:
        cat = ""
    else:
        cat = "category/" + cat
    if self.ismovie:
        u = domain + "/movies/%s/%s/%d" % (cat, self.sort, n)
    else:
        u = domain + "/shows/%s/%s/%d" % (cat, self.sort, n)
    n = n + 1
    page = self.download(u, referer=domain)
    movies = re.findall('<div class="front">.*?<img src="(.*?)" alt="(.*?)".*?<div class="back" data-ajax="true" data-id="(.*?)".*?<a href="(.*?)"', page, re.DOTALL)
    for movie in movies:
        img, name, _, link = movie
        art = {
               "icon": img,
               "thumb": img,
               "poster": img,
               }
        self.additem(name, link, {}, art)
    return n


def scrapeinfo(self, url):
    domain = "https://%s" % self.setting.getstr("domain")
    page = self.download(url, referer=domain)
    tree = htmlement.fromstring(page)
    poster = tree.find(".//div[@class='poster']/img")
    js = re.findall('<script type="application/ld\+json">(.*?)</script>', page)
    js = json.loads(js[0])
    info = {}
    art = {}
    info["mpaa"] = js.get("contentRating", "")
    if self.ismovie:
        info["title"] = js.get("name", "")
    else:
        info["tvshowtitle"] = js.get("name", "")
    info["plot"] = info["plotoutline"] = js.get("description", "")
    try:
        info["year"] = int(js.get("dateCreated", "1000-").split("-")[0])
    except Exception:
        pass
    info["genre"] = ""
    for genre in js.get("genre", []):
        info["genre"] += genre + ", "
    rate = js.get("aggregateRating", None)
    if rate:
        rate = rate.get("ratingValue", "0")
        info["rating"] = float(rate)
    if "image" in js:
        art["fanart"] = js["image"]
    if poster is not None:
        art["poster"] = art["thumb"] = art["icon"] = poster.get("data-src")
    direc = re.findall('p class="directors".*?<a.*?>(.*?)</a>', page, re.DOTALL)
    if direc:
        info["director"] = direc[0]
    stars = re.findall('<p class="actors">(.*?)</p>', page, re.DOTALL)
    cast = []
    if stars:
        for star in re.findall('<a.*?>(.*?)</a>', stars[0]):
            cast.append(star)
    info["cast"] = cast
    return info, art


def getseasons(self, url):
    domain = "https://%s" % self.setting.getstr("domain")
    page = self.download(url, referer=domain)
    tree = htmlement.fromstring(page)
    info, art = self.getcache(url, "show")
    seasons = tree.findall(".//p[@class='indent']/a")
    if not len(seasons):
        seasons = tree.findall(".//select[@class='season-dropdown']/option")
        for season in seasons:
            self.additem(season.text.title(), season.get("value"), info, art)
    else:
        for season in seasons:
            self.additem(season.text.title(), season.get("href"), info, art)


def getepisodes(self, show, url):
    domain = "https://%s" % self.setting.getstr("domain")
    tree = htmlement.fromstring(self.download(url, referer=domain))
    info, art = self.getcache(show, "show")
    for episode in tree.findall(".//div[@class='episode ']"):
        epiart = art.copy()
        epiinfo = info.copy()
        link = episode.find(".//h5[@class='episode-title']/a")
        title = link.text
        epiinfo["title"] = title
        numbers = re.search("s([0-9]*)\se([0-9]*)", title, re.IGNORECASE)
        if numbers:
            if numbers.group(1).isdigit():
                epiinfo["season"] = int(numbers.group(1))
            if numbers.group(2).isdigit():
                epiinfo["episode"] = int(numbers.group(2))
        thumb = episode.find(".//span")
        if thumb is not None:
            epiart["thumb"] = epiart["icon"] = thumb.get("data-img")
        self.additem(title, link.get("href"), epiinfo, epiart)


def cacheepisodes(self, url):
    domain = "https://%s" % self.setting.getstr("domain")
    tree = htmlement.fromstring(self.download(url, referer=domain))
    plot = tree.find(".//p[@class='desc']")
    aired = tree.find(".//span[@class='release']/")
    info = {}
    if plot is not None:
        info["plot"] = info["plotoutline"] = plot.text
    if aired is not None:
        try:
            aired = re.sub('(st|nd|rd|th)\,', "", aired.tail.split("@")[0].strip())
            aired = time.strptime(aired, "%B %d %Y")
            aired = time.strftime("%Y-%m-%d", aired)
            info["aired"] = aired
        except Exception:
            pass
    return info, {}


def geturls(self, url):
    domain = "https://%s" % self.setting.getstr("domain")
    page = self.download(url)
    header = {
        'X-Requested-With': 'XMLHttpRequest',
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "",
        "authorization": "Bearer false",
        "accept": "application/json, text/javascript, */*; q=0.01",
        }
    data = {}
    cookies = {"loggedOut": "1"}
    dom = domain.split("//")[1]
    for cookie in cj:
        if dom in cookie.domain:
            cookies[cookie.name] = cookie.value
            if cookie.name == "__utmx":
                header["authorization"] = "Bearer %s" % cookie.value
    if self.ismovie:
        data["action"] = "getMovieEmb"
    else:
        data["action"] = "getEpisodeEmb"
    data["elid"] = urllib.quote(str(int(time.time())).encode("base-64")[:-1])
    data["token"] = re.findall("var\s*tok\s*\=\s*'(.*?)'", page)[0]
    data["idEl"] = re.findall('elid\s*=\s*"(.*?)"', page)[0]
    cookies[data["idEl"]] = data["elid"]
    data["elid"] = urllib.quote(data["elid"])
    for name, value in cookies.iteritems():
        header["cookie"] += "%s=%s;" % (name, value)
    data["nopop"] = ""
    js = "%s/templates/cartoonhd/assets/scripts/videojs-flixanity.js" % domain
    js = self.download(js, referer=domain)
    js = re.search('gett\(epData\.epId\).*?baseurl\s*?\+\s*?"(.+?)"', js, re.DOTALL)
    embeds = self.download(domain + js.group(1), data=data, headers=header,
                           referer="https://www.cartoonhd.cz/movie/quiet-storm-the-ron-artest-story", method="POST")
    embeds = json.loads(embeds)
    videos = []
    if not isinstance(embeds, dict):
        return
    for vid, source in embeds.iteritems():
        link = iframe(source.get("embed", ""))
        if not link:
            continue
        if "google" in source["type"] or "blogspot" in source["type"]:
            qual = re.findall("\- ([0-9]*?)p", source["type"])
            if qual:
                videos.append([link, int(qual[0])])
        else:
            if "openload" in source["type"]:
                qual = 718
            else:
                qual = 719
            videos.append([link, qual])
    videos.sort(key=itemgetter(1), reverse=True)
    for vid, qual in videos:
        yield vid


def search(self, keyw):
    domain = "https://%s" % self.setting.getstr("domain")
    # search is broken on the site
    page = self.download(domain)
    token = re.findall("var\s*tok\s*=\s*'(.+?)'", page)[0]
    # setstr = "".join([random.choice(string.ascii_letters) for k in range(25)])
    d = {
        "q": keyw,
        "limit": 100,
        "timestamp": int(time.time() * 1000),
        "verifiedCheck": token,
        "set": setstr,
        # "rt": caesar(str(token) + set, 13),
        "rt": setstr,
        # "sl": md5.new(slk.encode("base-64")[:-1] + search).hexdigest()
        "sl": searchstr
        }
    page = self.download("https://api.%s/api/v1/%s%s" % (self.setting.getstr("domain"),
                                                         slkstr,
                                                         searchstr),
                         data=d,
                         referer=domain, method="POST")
    for result in json.loads(page):
        if "movie" not in result["meta"].lower() and self.ismovie or \
                "tv show" not in result["meta"].lower() and not self.ismovie:
            continue
        result["permalink"] = result["permalink"].replace("/show/", "/series/")
        link = domain + result["permalink"]
        art = {
               "icon": domain + result["image"],
               "thumb": domain + result["image"],
               }
        self.additem(result["title"], link, {}, art)


def getcategories(self):
    domain = "https://%s" % self.setting.getstr("domain")
    if self.ismovie:
        path = "/full-movies"
    else:
        path = "/tv-series"
    page = self.download(domain + path, referer=domain)
    tree = htmlement.fromstring(page)
    for node in tree.findall(".//select[@name='categories']/option"):
        cat = urlparse.urlparse(node.get("value")).path.split("/")[-1]
        self.additem(node.text, cat)
