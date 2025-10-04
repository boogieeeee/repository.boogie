'''
Created on Sep 23, 2022

@author: boogie
'''
import htmlement
import re

from tinyxbmc import tools
from tinyxbmc import mediaurl
from tinyxbmc import net
from tinyxbmc import proxy
from tinyxbmc.addon import kodisetting

from six.moves.urllib import parse

rgx1 = r"baseStreamUrl\s?\=\s?(?:\'|\")(.+?)(?:\'|\")"
rgx2 = r"window.mainSource\s?\=\s?\[(?:\'|\")(.+?)(?:\'|\")"
setting = kodisetting("service.vods.selcuk")
webproxy = proxy.getrandom()()


def geturl():
    entrypage = webproxy.get("https://%s/" % setting.getstr("domain"))
    for url in htmlement.fromstring(entrypage).findall(".//a"):
        url = url.get("href")
        if url and "selcuksportshd" in url:
            return url


def iteratechannels(mainurl):
    xpage = htmlement.fromstring(webproxy.get(mainurl))
    links = xpage.findall(".//div[@class='channels']/div[2]/.//a")
    for link in links:
        chname = tools.elementsrc(link.find(".//div[@class='name']"), exclude=[link.find(".//b")]).strip()
        chlink = link.get("data-url")
        if chlink.startswith("http"):
            yield chlink, chname


def parse1(url, page):
    baseurl = re.search(rgx1, page)
    if not baseurl:
        return
    up = parse.urlparse(url)
    params = dict(parse.parse_qsl(up.query))
    if "id" not in params:
        return
    return baseurl.group(1) + params["id"] + "/playlist.m3u8"


def parse2(page):
    mainsource = re.search(rgx2, page)
    if mainsource:
        return mainsource.group(1)


def getmedias(url, mainurl, isadaptive=True, direct=True):
    subpage = net.http(url, referer=mainurl)
    link = parse1(url, subpage) or parse2(subpage)
    if not link:
        return
    yield mediaurl.HlsUrl(link,
                          headers={"referer": "https://%s/" % parse.urlparse(url).netloc},
                          adaptive=isadaptive, ffmpegdirect=direct)
