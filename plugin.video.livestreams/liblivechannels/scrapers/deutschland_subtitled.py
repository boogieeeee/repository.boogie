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


from liblivechannels import scraper
import re
import json


class br(scraper):
    domain = "https://www.br.de"
    categories = ["Deutschland", "Subtitled"]
    title = u"BR [ÜT]"
    icon = domain + "/unternehmen/inhalt/rundfunkrat/br-fernsehen-logo-neu-102~_v-img__16__9__xl_-d31c35f8186ebeb80b0cd843a7c267a0e0c81647.jpg?version=2b06d"

    def get(self):
        page = self.download(self.domain + "/mediathek/live")
        link = re.search(r'publicLocation.+?"(.+?)"', page)
        yield link.group(1)


class daserste(scraper):
    domain = "https://live.daserste.de/"
    categories = ["Deutschland", "Subtitled"]
    title = u"Das Erste [ÜT]"
    icon = domain + "/mediasrc/img/tv/ard/ard-daserste-logo.png"

    def get(self):
        page = self.download(self.domain)
        js = re.search(r'data-ctrl-player="(.+?)"', page).group(1)
        js = re.search(r'url(?:\'|\")\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")', js).group(1)
        jsdata = json.loads(self.download(self.domain + js, referer=self.domain))
        yield jsdata["mc"]["_alternativeMediaArray"][0]["_mediaArray"][0]["_mediaStreamArray"][0]["_stream"][0]
