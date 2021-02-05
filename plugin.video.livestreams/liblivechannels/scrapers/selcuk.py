# -*- encoding: utf-8 -*-
from liblivechannels import scraper, scrapers
from tinyxbmc import tools
from tinyxbmc import net

from scrapertools import yayinakisi
import urlparse
import json

from liblivechannels import config

import htmlement

cfg = config.config()


class sel_chan(scraper):
    subchannel = True
    categories = ["sport", "selcukspor"]

    def get(self):
        chid = dict(urlparse.parse_qsl(urlparse.urlparse(self.url).query)).get("id")
        up = urlparse.urlparse(self.url)
        jsurl = "%s://%s/dmzjsn.json" % (up.scheme, up.netloc)
        sdomain = json.loads(self.download(jsurl, referer=self.url, headers={"x-requested-with": "XMLHttpRequest"}))["d"]
        media = "https://xx.%s/kaynakstreamradarco/%s/strmrdr.m3u8" % (sdomain, chid)
        yield net.tokodiurl(media, headers={"referer": self.url})

    def iterprogrammes(self):
        for prog in yayinakisi.iterprogramme(self.title):
            yield prog


class selcuk(scrapers):
    def iteratechannels(self):
        xpage = htmlement.fromstring(self.download(cfg.selcuk))
        for a in xpage.iterfind(".//div[@id='b-tv']/.//a"):
            href = net.absurl(a.get("href").split("#")[0], cfg.selcuk)
            chname = tools.elementsrc(a, exclude=[a.find(".//b")]).strip()
            chid = json.dumps([href, chname])
            yield self.makechannel(chid, sel_chan, url=href, title=chname)

    def getchannel(self, cid):
        url, chname = json.loads(cid)
        return self.makechannel(cid, sel_chan, url=url, title=chname)
