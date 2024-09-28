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
rgx1 = r"\s*[a-z]+\s?\:\s?(?:\'|\")(.+?)(?:\'|\")"
rgx2 = r"window\.streamradardomil\s*?\=\s*?(.+?)\;"
rgx3 = r"window\.streamradardomil\s*?\=\s*?(.+?)\;"
rgx4 = r"atob\((?:\"|\')([a-zA-Z0-9\=]+?)(?:\"|\')\)"
rgx5 = r"window._[a-f0-9]+\s*?\=\s*?window\[.atob.\]\((?:\'|\")([A-Za-z0-9\=]+)(?:\'|\")"
rgx6 = r"src\s*?\=\s*?(?:\"|\')(\/keslanorospu.+?)(?:\"|\')"
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
            chlink = chlink.split("#")[0]
            up = parse.urlparse(chlink)
            chdict = dict(parse.parse_qsl(up.query))
            if "id" in chdict:
                yield chdict["id"], chlink, chname


def getmedias(chid, mainurl, isadaptive=False, direct=False):
    for _chid, url, _chname in iteratechannels(mainurl):
        if _chid == chid:
            subpage = net.http(url, referer=mainurl)
            bases = [base64.b64decode(x).decode() for x in re.findall(rgx4, subpage)]
            _data1 = bases.pop(0)
            _reklam = bases.pop(0)
            _iframe = bases.pop(-1)
            doms = bases.pop(-1), bases.pop(-1)
            subs = bases
            for sub in subs:
                media = f"https://{sub}{doms[0]}/i/{parse.urlparse(mainurl).netloc}/{chid}/playlist.m3u8"
                yield mediaurl.hlsurl(media, headers={"referer": "https://%s/" % parse.urlparse(url).netloc}, adaptive=isadaptive, ffmpegdirect=direct)
            break
