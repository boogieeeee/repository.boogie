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
from tinyxbmc import net
from tinyxbmc import const


class dogan(object):
    dataid = None
    xpath = None

    def checkalive(self):
        page = self.download(self.yayin, referer=self.domain)
        for div in htmlement.fromstring(page).findall(self.xpath):
            dataid = div.get("data-id")
            if dataid:
                self.dataid = dataid
                break
        return self.dataid

    def get(self):
        self.checkalive()
        u = self.jsurl % (self.domain, self.dataid)
        page = self.download(u, referer=self.yayin)
        js = json.loads(page)
        serviceurl = js["Media"]["Link"]["ServiceUrl"]
        if serviceurl == "":
            serviceurl = js["Media"]["Link"]["DefaultServiceUrl"]
        securepath = js["Media"]["Link"]["SecurePath"]
        if securepath.startswith("https://"):
            link = securepath
        else:
            link = serviceurl + "/" + securepath
        yield net.tokodiurl(link, None, {"Referer": self.yayin, "User-agent": const.USERAGENT})


class cnnturk(dogan, scraper):
    categories = ["Turkish", "News", "Turkey"]
    title = u"CNN Türk"
    domain = "https://www.cnnturk.com"
    icon = "http://www.gundemgazetesi.net/d/other/cnn_t_rk-001.png"
    xpath = ".//div[@data-category='canli-yayin']"
    yayin = domain + "/canli-yayin"
    jsurl = "%s/action/media/%s"


"""
class kanald(scraper):
    categories = ["Turkish", "Entertainment", "Turkey"]
    title = "Kanal D"
    domain = "https://www.kanald.com.tr"
    icon = "https://i.pinimg.com/originals/c9/a2/9f/c9a29f88e61fe3dbe392b37a1e208185.png"
    xpath = ".//div[@ng-controller='PlayerCtrl']"
    yayin = domain + "/canli-yayin"
    jsurl = "%s/actions/content/media/%s"

"""