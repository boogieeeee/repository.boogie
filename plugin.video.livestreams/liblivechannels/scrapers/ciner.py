# -*- coding: utf-8 -*-
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

from liblivechannels import scraper
import htmlement
import json


class ciner(object):
    xpath = './/div[@class="htplay_video"]'

    def checkalive(self):
        tree = htmlement.fromstring(self.download(self.live, referer=self.domain))
        for div in tree.findall(self.xpath):
            data = div.get("data-ht")
            if data:
                self.m3u8 = json.loads(data)["ht_stream_m3u8"]
        return self.m3u8

    def get(self):
        if not self.m3u8:
            self.checkalive()
        yield self.m3u8


class haberturk(ciner, scraper):
    domain = "http://www.haberturk.com/"
    live = "%s/canliyayin" % domain
    categories = ["Turkish", "Turkey", "News"]
    title = u"HaberTürk"
    icon = "https://lh3.googleusercontent.com/RHV4WLdQNalCG87rSH5Q60ZDEnHMg1_Az679Dg6DglSinOxdyD3W80VLpn7SlSjd1Q=w300"
    m3u8 = None


class showtv(ciner, scraper):
    domain = "http://www.showtv.com.tr/"
    live = "%s/canli-yayin" % domain
    categories = ["Turkish", "Turkey", "Entertainment"]
    title = "Show TV"
    icon = "https://yt3.ggpht.com/a/AGF-l7-pbSxRH989aWGOuLgMyn41zkxdi-GTUlbfqA=s288-mo-c-c0xffffffff-rj-k-no"
    m3u8 = None
    xpath = xpath = './/div[@class="htplay"]'


class bloobmberght(ciner, scraper):
    domain = "http://www.bloomberght.com"
    live = "%s/tv" % domain
    categories = ["Turkish", "Turkey", "News", "Finance"]
    title = "Bloomberg HT"
    icon = "http://www.bloomberght.com/images/logo.png"
    m3u8 = None
