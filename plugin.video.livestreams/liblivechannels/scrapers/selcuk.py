# -*- encoding: utf-8 -*-
'''
    Author    : Huseyin BIYIK <husenbiyik at hotmail>
    Year      : 2016
    License   : GPL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


from liblivechannels import scraper, scrapers
from tinyxbmc import tools
from tinyxbmc import net
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
