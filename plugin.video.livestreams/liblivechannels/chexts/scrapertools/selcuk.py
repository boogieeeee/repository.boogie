# -*- encoding: utf-8 -*-
from tinyxbmc import tools
from tinyxbmc import net

from liblivechannels.chexts.scrapertools import normalize
import urlparse
import json
import re

from liblivechannels import config

import htmlement

cfg = config.config()

maxlink = 5

subpath = None


def iteratechannels():
    found = False
    up = urlparse.urlparse(cfg.selcuk)
    domnum = int(re.search("[0-9]+", up.netloc).group(0))
    for linkcnt in range(maxlink):
        netloc = re.sub("[0-9]+", str(domnum + linkcnt), up.netloc)
        url = "%s://%s" % (up.scheme, netloc)
        xpage = htmlement.fromstring(net.http(url, cache=10))
        links = xpage.findall(".//div[@id='b-tv']/.//a")
        if links:
            found = True
            break
    if not cfg.selcuk == url:
        cfg.selcuk = url
    if not found:
        print "selcuk url is wrong"
    else:
        for link in links:
            chname = tools.elementsrc(link, exclude=[link.find(".//b")]).strip()
            yield link.get("href"), chname


def itermedias(chfilter):
    if chfilter:
        found = False
        for url, chname in iteratechannels():
            if chfilter == normalize(chname):
                found = True
                break
        if found:
            links = url.split("#")
            up = urlparse.urlparse(links[0])
            chdict = dict(urlparse.parse_qsl(up.query))
            if "id" in chdict:
                subpage = net.http(links[0], referer=cfg.selcuk)
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
                    subpath = re.search("dmz[a-zA-Z0-9]+?\+(?:\'|\")(.+?)(?:\'|\")", net.http(kourl, referer=cfg.selcuk)).group(1)
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
                subpage = net.http(links[0], referer=cfg.selcuk)
                media = re.findall("window.mainSource\s*?\=\s*?\[(?:\'|\")(.+?)(?:\'|\")", subpage)[0]
            yield net.tokodiurl(media, headers={"referer": url})
