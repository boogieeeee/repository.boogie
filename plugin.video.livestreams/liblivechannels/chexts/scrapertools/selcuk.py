# -*- encoding: utf-8 -*-
try:
    import unittest
    import test

    class TestChannel(unittest.TestCase):
        def test_list(self):
            chans = len(list(iteratechannels()))
            self.assertTrue(chans > 0, "Selcuk found %s number of channels" % chans)
except ImportError:
    pass


from tinyxbmc import tools
from tinyxbmc import net

from six.moves.urllib import parse
from liblivechannels.chexts.scrapertools import normalize
from thirdparty import packed
import json
import re
import htmlement
import base64


maxlink = 5
subpath = None
girisurl = "https://giris1.selcuksportshdgiris13.com/"


def iteratechannels():
    entrypage = net.http(girisurl, cache=10)
    url = htmlement.fromstring(entrypage).findall(".//div[@class='sites']/.//a")[0].get("href")
    xpage = htmlement.fromstring(net.http(url, cache=10))
    links = xpage.findall(".//div[@class='channels']/.//div[@id='tab5']/.//a")
    for link in links:
        chname = tools.elementsrc(link.find(".//div[@class='name']"), exclude=[link.find(".//b")]).strip()
        yield url, link.get("data-url"), chname


def method3(subpage):
    yield re.search("window\.mainSource[\s\t]*?\=[\s\t]*?\[(?:\"|\')(.+?)(?:\"|\')\]", subpage).group(1)


def method1(page, subpath, chid):
    for embed in re.findall("window.atob\(\"(.*?)\"\)", page):
        jsdata = json.loads(base64.b64decode(embed).decode())
        yield "https://xxx.%s%s%s/strmrdr.m3u8" % (jsdata["d"], subpath, chid)
        break


def method2(up, url, chid):
    jsurl = "%s://%s/dmzjsn.json" % (up.scheme, up.netloc)
    sdomain = json.loads(net.http(jsurl, referer=url, headers={"x-requested-with": "XMLHttpRequest"}))["d"]
    yield "https://xxx.%s%s%s/strmrdr.m3u8" % (sdomain, subpath, chid)


def itermedias(chfilter, isadaptive=True):
    if chfilter:
        found = False
        for selcukurl, url, chname in iteratechannels():
            if chfilter == normalize(chname):
                found = True
                break
        if found:
            links = url.split("#")
            up = parse.urlparse(links[0])
            chdict = dict(parse.parse_qsl(up.query))
            if "id" in chdict:
                subpage = net.http(links[0], referer=selcukurl)
                chid = chdict.get("id")
                kourl = "%s://%s/keslanorospucocugu.js" % (up.scheme, up.netloc)
                try:
                    subpath = re.search("dmz[a-zA-Z0-9]+?\+(?:\'|\")(.+?)(?:\'|\")", net.http(kourl, referer=selcukurl)).group(1)
                except Exception:
                    subpath = None
                found = False
                media = None
                for method in method3(subpage), method1(subpage, subpath, chid), method2(up, url, chid):
                    for vid in tools.safeiter(method):
                        media = vid
                        break
                    if media:
                        break
            yield net.hlsurl(media, headers={"referer": url}, adaptive=isadaptive)
