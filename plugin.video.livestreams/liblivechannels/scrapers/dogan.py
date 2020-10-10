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
import htmlement
import json

from liblivechannels import scraper
from tinyxbmc import net
from tinyxbmc import const
from tinyxbmc import tools

import ecanli
import scrapertools


class dogan(object):
    dataid = None
    xpath = None

    def get(self):
        with tools.ignoreexception():
            page = self.download(self.yayin, referer=self.domain)
            for div in htmlement.fromstring(page).findall(self.xpath):
                dataid = div.get("data-id")
                if dataid:
                    self.dataid = dataid
                    break
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
        for media in ecanli.iterexternal(self.download, self.title):
            yield media


class cnnturk(dogan, scraper):
    categories = ["Turkish", "News", "Turkey"]
    title = u"CNN Türk"
    domain = "http://www.cnnturk.com"
    icon = "http://www.gundemgazetesi.net/d/other/cnn_t_rk-001.png"
    xpath = ".//div[@data-category='canli-yayin']"
    yayin = domain + "/canli-yayin"
    jsurl = "%s/action/media/%s"

    def iterprogrammes(self):
        tree = htmlement.fromstring(self.download("%s/yayin-akisi" % self.domain))
        datepsr = scrapertools.dateparser(3, shiftdate=False)
        pitr = scrapertools.makeprograms(datepsr.datefromhour(0, 0, 0, 1))
        oldhour = 0
        dayshift = - datepsr.loc_now.weekday()
        for div in tree.iterfind(".//div[@class='guide-wrapper']/div/div"):
            dclass = div.get("class")
            if dclass is not None and "program" in dclass:
                hourtag = div.find(".//span[@class='time']")
                if hourtag is None:
                    continue
                hour, minute = hourtag.text.split(":")
                if oldhour > hour:
                    dayshift += 1
                oldhour = hour
                img_tag = div.find(".//img")
                img = img_tag.get("data-src").replace("80x80", "200x200")
                title = img_tag.get("alt")
                yield pitr.add(title, datepsr.datefromhour(hour, minute, daydelta=dayshift), icon=img)
        yield pitr.flush()


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
