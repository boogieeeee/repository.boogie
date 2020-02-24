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

"""
totally broken

from liblivechannels import scraper
import re
import json


class turkuaz(object):
    def processlink(self, link):
        return link

    def checkalive(self):
        page = self.vods.download(self.js, referer=self.yayin)
        r = re.search("url\:\s?.*(?:'|\")(.+?)(?:'|\")", page)
        if r:
            self.m3u8 = self.processlink(r.group(1))
        return self.m3u8

    def get(self):
        if not self.m3u8:
            self.checkalive()
        url = "%s|%s" % (json.loads(self.vods.download(self.m3u8, referer=self.yayin))["Url"],
                         self.yayin)
        yield url


class atv(turkuaz, scraper):
    domain = "https://www.atv.com.tr"
    yayin = "%s/webtv/canli-yayin" % domain
    js = "https://iatv.tmgrup.com.tr/site/v1/j/video.js?v=9.5"
    title = "ATV"
    icon = "http://www.globya.com.tr/wp-content/uploads/2016/03/clients-06.png"
    m3u8 = None
    categories = ["Turkish", "Entertainment", "Turkey"]


class ahaber(turkuaz, scraper):
    domain = "https://www.ahaber.com.tr"
    yayin = "%s/webtv/canli-yayin" % domain
    js = yayin
    title = "A Haber"
    icon = "https://iahbr.tmgrup.com.tr/site/v2/i/ahaber-facebook-logo.png"
    m3u8 = None
    categories = ["Turkish", "News", "Turkey"]


class minikago(turkuaz, scraper):
    domain = "http://www.minikago.com.tr"
    yayin = "%s/webtv/canli-yayin" % domain
    js = yayin
    title = "MinikaGO"
    icon = "http://i.minika.com.tr/go/v1/i/goLogo.png"
    m3u8 = None
    categories = ["Turkish", "Kids", "Turkey"]

    def processlink(self, link):
        return "https://securevideotoken" + link


class atvavrupa(turkuaz, scraper):
    domain = "http://www.atvavrupa.tv"
    yayin = "%s/webtv/canli-yayin" % domain
    js = yayin
    title = "ATV Avrupa"
    icon = "http://dmedya.com/wp-content/uploads/2017/03/atv-avrupa-tv-logo-png-300x200.png"
    m3u8 = None
    categories = ["Turkish", "Entertainment", "Turkey"]

    def processlink(self, link):
        return "https://securevideotoken" + link


class atvspor(turkuaz, scraper):
    domain = "https://www.aspor.com.tr"
    yayin = "%s/webtv/canli-yayin" % domain
    js = yayin
    title = "A Spor"
    icon = "https://iaspr.tmgrup.com.tr/site/v2/i/aspor-logo-2.png"
    m3u8 = None
    categories = ["Turkish", "Sport", "Turkey"]

    def processlink(self, link):
        return "https://securevideotoken" + link


class anews(turkuaz, scraper):
    domain = "http://www.anews.com.tr"
    yayin = "%s/webtv/live-broadcast" % domain
    js = yayin
    title = "A News"
    icon = "http://i.tmgrup.com.tr/anews/v1/i/logo-anews.png"
    m3u8 = None
    categories = ["English", "News", "Turkey"]

    def processlink(self, link):
        return "https://securevideotoken" + link
        
"""