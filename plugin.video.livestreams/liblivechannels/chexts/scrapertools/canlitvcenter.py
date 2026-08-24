'''
Created on Aug 2, 2021

@author: boogie
'''
try:
    import unittest
    import test

    class testcanli(unittest.TestCase):
        def test_canli_link(self):
            test.testlink(self, itermedias("trt 1"), 1, "trt 1", 0)

except ImportError:
    pass

from tinyxbmc import net
from tinyxbmc import mediaurl
from tinyxbmc import tools

import re
import htmlement
import traceback


dom = "canlitv.center"
domain = "https://" + dom
RGX_MEDIA = r"embedUrl(?:\'|\")\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")"


def api(yayin, ref, base):
    if not yayin:
        return
    splits = yayin.split(":")
    if not len(splits) == 2 or splits[1][:2] == "//":
        return yayin
    bot, chanid = splits
    if bot == "gini":
        return yayin
    aurl = f"{base}/api/bot/{bot}"
    error = None
    js = {}
    try:
        js = net.http(aurl, params={"id": chanid}, referer=ref, json=True)
        error = js.get("error")
        yayin = js["stream_url"]
    except Exception:
        print(error, traceback.format_exc(), aurl, chanid)
    if js.get("status") == "error":
        print(js.get("message"), aurl, chanid)
    return yayin


def itermedias(kw):
    resp = net.http("https://" + dom, text=False)
    url = resp.url
    search = net.http(url + "/arama", params={"search": kw})
    lsearch = htmlement.fromstring(search)
    kwtag = kw.lower().replace("tv", "").replace(" ", "")
    for a in lsearch.iterfind(".//div[@class='isim']/.//a"):
        chtag = tools.elementsrc(a).lower().replace("tv", "").replace(" ", "")
        if chtag == kwtag:
            u = net.absurl(a.get("href"), url)
            sources = [net.http(u, referer=domain)]
            for mirror in htmlement.fromstring(sources[0]).iterfind(".//ul[@class='buttons']/.//a"):
                href = mirror.get("href")
                if not href:
                    continue
                href = net.absurl(href, url)
                if not href.startswith(u) or u == href:
                    continue
                sources.append(net.http(href, referer=domain))
            for source in sources:
                yayin = re.search(RGX_MEDIA, source).group(1)
                yayin = api(yayin, u, url)
                yield mediaurl.HlsUrl(yayin, headers={"referer": u}, adaptive=True, ffmpegdirect=False)
