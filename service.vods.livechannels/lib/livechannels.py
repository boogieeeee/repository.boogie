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

import vods

import liblivechannels
import urlparse
from tinyxbmc import tools
from tinyxbmc import gui


class livechannels(vods.movieextension):
    uselinkplayers = False
    useaddonplayers = True

    @property
    def validate(self):
        return self.setting.getbool("validate")

    @validate.setter
    def validate(self, value):
        self.setting.set("validate", value)

    def getcategories(self):
        for cat in tools.safeiter(liblivechannels.getcategories()):
            self.additem(cat, cat)

    def headcheck(self, url):
        headers = {}
        urls = url.split("|")
        if len(urls) == 2:
            url = urls[0]
            headers = dict(urlparse.parse_qsl(urls[1]))
        try:
            response = self.download(url, headers=headers, method="HEAD", timeout=2)
            if not response.status_code == 200:
                return "HTTP ERROR : %s" % response.status_code
        except Exception, e:
            return str(e)

    def getmovies(self, cat=None):
        if not cat:
            cat = []
        else:
            cat = [cat]
        ccache = self.hay("livechannelsdb")
        channels = ccache.find("channels").data
        if self.validate or not channels.get("alives"):
            chans = tools.safeiter(liblivechannels.iterchannels(*cat))
            channels = {"alives": []}
            ccache.burn()
            pg = gui.progress("Checking")
            pg.update(0, "Loading Channels")
            chans = list(chans)
            index = 0
            for chan in chans:
                if pg.iscanceled():
                    break
                valid = False
                c = liblivechannels.loadchannel(chan, self)
                index += 1
                error = "No links"
                if c.checkerrors is not None:
                    error = c.checkerrors()
                    if error is None:
                        channels["alives"].append([c.icon, c.title, c.index])
                        pg.update(100 * index / len(chans), c.title, "UP", c.index)
                        continue
                for url in tools.safeiter(c.get()):
                    error = self.headcheck(url)
                    if error is None:
                        channels["alives"].append([c.icon, c.title, c.index])
                        valid = True
                        pg.update(100 * index / len(chans), c.title, "UP", c.index)
                        break
                if not valid:
                    pg.update(100 * index / len(chans), c.title, error, c.index)
                if index == 200000:
                    break
            ccache.throw("channels", channels)
            pg.close()
            self.validate = False
        for icon, title, index in channels.get("alives", []):
            info = {"title": title}
            art = {"icon": icon, "thumb": icon, "poster": icon}
            self.additem(title, index, info, art)

    def geturls(self, cid):
        chan = liblivechannels.loadchannel(cid, self)
        self.uselinkplayers = chan.uselinkplayers
        self.useaddonplayers = chan.useaddonplayers
        for url in chan.get():
            yield url

    def searchmovies(self, keyword):
        pass
