# -*- encoding: utf-8 -*-
try:
    import unittest
    import test

    class TestSelcuk(unittest.TestCase):
        def test_selcuk_list(self):
            chans = len(list(iteratechannels()))
            self.assertTrue(chans > 0, "Selcuk found %s number of channels" % chans)

        def test_selcuk_link(self):
            test.testlink(self, itermedias("bein1"), 1, "bein1", 0)

        def test_selcuk_mlink(self):
            test.testlink(self, mobile_itermedias("36"), 1, "nat geo wild", 0)

except ImportError:
    pass

from tinyxbmc import tools
from tinyxbmc import net

from six.moves.urllib import parse
from liblivechannels.chexts.scrapertools import normalize
import re
import htmlement
import base64


maxlink = 5
subpath = None
girisurl = "https://giris1.selcuksportshdgiris13.com/"
rgx1 = "\s*[a-z]+\s?\:\s?(?:\'|\")(.+?)(?:\'|\")"
rgx2 = "window\.streamradardomil\s*?\=\s*?(.+?)\;"
rgx3 = "window\.streamradardomil\s*?\=\s*?(.+?)\;"
rgx4 = "atob\((?:\"|\')([a-zA-Z0-9\=]+?)(?:\"|\')\)"
rgx5 = "window._[a-f0-9]+\s*?\=\s*?window\[.atob.\]\((?:\'|\")([A-Za-z0-9\=]+)(?:\'|\")"
rgx6 = "src\s*?\=\s*?(?:\"|\')(\/keslanorospu.+?)(?:\"|\')"


def iteratechannels():
    entrypage = net.http(girisurl, cache=10)
    url = htmlement.fromstring(entrypage).findall(".//div[@class='sites']/.//a")[0].get("href")
    xpage = htmlement.fromstring(net.http(url, cache=10))
    links = xpage.findall(".//div[@class='channels']/.//div[@id='tab5']/.//a")
    for link in links:
        chname = tools.elementsrc(link.find(".//div[@class='name']"), exclude=[link.find(".//b")]).strip()
        yield url, link.get("data-url"), chname


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
                subpage = net.http(links[0], referer=selcukurl, cache=None)
                olmusmu = re.findall(rgx1, subpage)
                if len(olmusmu) == 3:
                    # olmusmu = [parse.unquote(x) for x in olmusmu]
                    keslan = re.search(rgx6, subpage)
                    kourl = "%s://%s/%s" % (up.scheme, up.netloc, keslan.group(1))
                    kopage = net.http(kourl, referer=selcukurl, cache=None)
                    bases = [base64.b64decode(x).decode() for x in re.findall(rgx4, kopage)]
                    _radardom = bases.pop(-1)
                    selcukdom = bases.pop(-1)
                    for base in bases:
                        if "." not in base:
                            media = "https://" + base + selcukdom + "/i/" + olmusmu[-1] + "/" + chdict["id"] + "/playlist.m3u8" + olmusmu[-2]
                            yield net.hlsurl(media, headers={"referer": url}, adaptive=isadaptive)


def mobile_itermedias(chid, isadaptive=True):
    # https://app.selcuksportsappltf.com/app/belgesel.json
    mdom = "https://app.selcuksportsappltf.com/app/"
    jsu = "%skanal/%s.json" % (mdom, chid)
    js = net.http(jsu, json=True)
    for result in js.get("results", []):
        m3u = result.get("m3u8_url")
        if m3u:
            yield net.hlsurl(m3u, adaptive=isadaptive)
