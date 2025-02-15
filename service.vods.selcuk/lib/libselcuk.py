'''
Created on Sep 23, 2022

@author: boogie
'''
import htmlement
import re
import base64
import json

from tinyxbmc import tools
from tinyxbmc import mediaurl
from tinyxbmc import net
from tinyxbmc.addon import kodisetting

from six.moves.urllib import parse

rgx1 = r"baseStreamUrl\s?\=\s?(?:\'|\")(.+?)(?:\'|\")"
rgx2 = r"window.mainSource\s?\=\s?\[(?:\'|\")(.+?)(?:\'|\")"
setting = kodisetting("service.vods.selcuk")


def geturl():
    entrypage = net.http("https://%s/" % setting.getstr("domain"), cache=10)
    return htmlement.fromstring(entrypage).findall(".//a[@class='button']")[0].get("href")


def iteratechannels(mainurl):
    xpage = htmlement.fromstring(net.http(mainurl, cache=None))
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


def getmedias(url, mainurl, isadaptive=False, direct=False):
    subpage = net.http(url, referer=mainurl)
    link = parse1(url, subpage) or parse2(subpage)
    if not link:
        return
    yield mediaurl.hlsurl(link,
                          headers={"referer": "https://%s/" % parse.urlparse(url).netloc},
                          adaptive=isadaptive, ffmpegdirect=direct)
