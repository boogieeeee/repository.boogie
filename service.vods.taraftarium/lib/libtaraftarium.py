'''
Created on Sep 23, 2022

@author: boogie
'''
import htmlement
import re

from tinyxbmc import tools
from tinyxbmc import mediaurl
from tinyxbmc import net
from tinyxbmc.addon import kodisetting

from six.moves.urllib import parse

SETTING = kodisetting("service.vods.taraftarium")
DOMAIN = SETTING.getstr("domain")
MAINURL = f"https://{DOMAIN}"
RGX1 = r"baseurl\s*?\=\s*?(?:\"|\')(.+?)(?:\"|\')"


def makekeyw(txt):
    repls = [" "]
    for repl in repls:
        txt = txt.replace(repl, "")
    return txt.lower().strip()


def iteratechannels():
    page = net.http(MAINURL)
    xpage = htmlement.fromstring(page)
    for div in xpage.iterfind(".//div[@class='macListe']/div"):
        chname = tools.elementsrc(div.find(".//span[@class='takimlar']")).strip()
        link = div.get("data-url")
        yield link, chname


def geturls(link):
    subpage = net.http(link, referer=MAINURL)
    baseurl = re.search(RGX1, subpage).group(1)
    up = parse.urlparse(link)
    origin = f"{up.scheme}://{up.netloc}"
    referer = origin + "/"
    params = dict(parse.parse_qsl(up.query))
    streamid = params["id"]
    url = baseurl + streamid + ".m3u8"
    yield mediaurl.HlsUrl(url, headers={"referer": referer, "origin": origin})


def geturlsfromchannel(chid):
    chid = makekeyw(chid)
    for link, chname in iteratechannels():
        if chid not in makekeyw(chname):
            continue
        for media in geturls(link):
            yield media
        break
