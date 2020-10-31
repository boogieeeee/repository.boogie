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
import re

from liblivechannels import scraper
from tinyxbmc import net


domain = "https://www.dmax.com.tr"

class dmax(scraper):
    title = u"DMAX"
    categories = [u"Türkçe", u"Realiti"]
    icon = domain + "/assets/theme/assets/images/white_logo.png"
    usehlsproxy = False

    def get(self):
        u = domain + "/canli-izle"
        pg = self.download(u, referer=domain)
        rgx = 'liveUrl\s*?=\s*?"(.+?)"'
        jsu = re.search(rgx, pg).group(1)
        js = self.download(jsu.replace("/dmax?", "/dmaxdai?") + "&json=true", referer=u, json=True)
        yield net.tokodiurl(js["xtra"]["url"], headers={"Referer": u})
        
