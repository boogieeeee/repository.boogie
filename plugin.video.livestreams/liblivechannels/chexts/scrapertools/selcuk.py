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

from liblivechannels.chexts.scrapertools import normalize
import urlparse
import json
import re
import htmlement


maxlink = 5
subpath = None
girisurl = "https://giris2.selcuksportshdgiris2.com/"


def iteratechannels():
    entrypage = net.http(girisurl, cache=10)
    url = htmlement.fromstring(entrypage).findall(".//div[@class='sites']/.//a")[0].get("href")
    xpage = htmlement.fromstring(net.http(url, cache=10))
    links = xpage.findall(".//div[@id='b-tv']/.//a")
    for link in links:
        chname = tools.elementsrc(link, exclude=[link.find(".//b")]).strip()
        yield url, link.get("href"), chname


def itermedias(chfilter):
    if chfilter:
        found = False
        for selcukurl, url, chname in iteratechannels():
            if chfilter == normalize(chname):
                found = True
                break
        if found:
            links = url.split("#")
            up = urlparse.urlparse(links[0])
            chdict = dict(urlparse.parse_qsl(up.query))
            if "id" in chdict:
                subpage = net.http(links[0], referer=selcukurl)
                embeds = re.findall("window\[\\'atob\\']\(\"(.+?)\"\)", subpage)
                media = None
                if len(embeds) == 2 and len(embeds[1]) > 10:
                    try:
                        media = embeds[1].decode("base64")
                    except Exception:
                        pass
                if not media:
                    chid = chdict.get("id")
                    kourl = "%s://%s/keslanorospucocugu.js" % (up.scheme, up.netloc)
                    subpath = re.search("dmz[a-zA-Z0-9]+?\+(?:\'|\")(.+?)(?:\'|\")", net.http(kourl, referer=selcukurl)).group(1)
                    jsurl = "%s://%s/dmzjsn.json" % (up.scheme, up.netloc)
                    sdomain = json.loads(net.http(jsurl, referer=url, headers={"x-requested-with": "XMLHttpRequest"}))["d"]
                    media = "https://xxx.%s%s%s/strmrdr.m3u8" % (sdomain, subpath, chid)
            elif "stream" in chdict:
                strid = chdict.get("stream")
                up = urlparse.urlparse(links[1])
                jsurl = "%s://%s/dmzjsn.json" % (up.scheme, up.netloc)
                sdomain = json.loads(net.http(jsurl, referer=url, headers={"x-requested-with": "XMLHttpRequest"}))["d"]
                media = "https://srvb.%s/kaynakstreamradarco/%s/strmrdr.m3u8" % (sdomain, strid)
            else:
                # this may not happen always
                subpage = net.http(links[0], referer=selcukurl)
                media = re.findall("window.mainSource\s*?\=\s*?\[(?:\'|\")(.+?)(?:\'|\")", subpage)[0]
            yield net.tokodiurl(media, headers={"referer": url})
