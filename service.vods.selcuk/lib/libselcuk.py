'''
Created on Sep 23, 2022

@author: boogie
'''
import htmlement
import re
import base64

from tinyxbmc import tools
from tinyxbmc import mediaurl
from tinyxbmc import net
from tinyxbmc.addon import kodisetting

from six.moves.urllib import parse

maxlink = 5
subpath = None
rgx1 = "\s*[a-z]+\s?\:\s?(?:\'|\")(.+?)(?:\'|\")"
rgx2 = "window\.streamradardomil\s*?\=\s*?(.+?)\;"
rgx3 = "window\.streamradardomil\s*?\=\s*?(.+?)\;"
rgx4 = "atob\((?:\"|\')([a-zA-Z0-9\=]+?)(?:\"|\')\)"
rgx5 = "window._[a-f0-9]+\s*?\=\s*?window\[.atob.\]\((?:\'|\")([A-Za-z0-9\=]+)(?:\'|\")"
rgx6 = "src\s*?\=\s*?(?:\"|\')(\/keslanorospu.+?)(?:\"|\')"
setting = kodisetting("service.vods.selcuk")


def geturl():
    entrypage = net.http("https://%s/" % setting.getstr("domain"), cache=10)
    return htmlement.fromstring(entrypage).findall(".//a[@class='button']")[0].get("href")


def iteratechannels():
    xpage = htmlement.fromstring(net.http(geturl(), cache=None))
    links = xpage.findall(".//div[@class='channels']/div[2]/.//a")
    for link in links:
        chname = tools.elementsrc(link.find(".//div[@class='name']"), exclude=[link.find(".//b")]).strip()
        chlink = link.get("data-url")
        if chlink.startswith("http"):
            chlink = chlink.split("#")[0]
            up = parse.urlparse(chlink)
            chdict = dict(parse.parse_qsl(up.query))
            if "id" in chdict:
                yield chdict["id"], chlink, chname


def getmedias(chid, isadaptive=False, direct=False):
    for _chid, url, _chname in iteratechannels():
        if _chid == chid:
            subpage = net.http(url, referer=geturl(), cache=None)
            olmusmu = re.findall(rgx1, subpage)
            if len(olmusmu) >= 3:
                olmusmu = olmusmu[-3:]
                #keslan = re.search(rgx6, subpage)
                #kourl = "%s://%s/%s" % (up.scheme, up.netloc, keslan.group(1))
                #kopage = net.http(kourl, referer=selcukurl, cache=None)
                bases = [base64.b64decode(x).decode() for x in re.findall(rgx4, subpage)]
                _data1 = bases.pop(0)
                _reklam = bases.pop(0)
                _iframe = bases.pop(-1)
                doms = bases.pop(-1), bases.pop(-1)
                subs = bases
                for sub in subs:
                    media = "https://" + sub + doms[0] + "/selcuksports/" + olmusmu[-1] + "/" + chid + "/playlist.m3u8" + olmusmu[-2]
                    yield mediaurl.hlsurl(media, headers={"referer": "https://%s/" % parse.urlparse(url).netloc}, adaptive=isadaptive, ffmpegdirect=direct)
            break
