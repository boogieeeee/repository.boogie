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

from tinyxbmc import container
from tinyxbmc import tools
from tinyxbmc import const
from tinyxbmc import net
from tinyxbmc import gui
from tinyxbmc import addon

import liblivechannels
from liblivechannels import common

from thirdparty import m3u8


class Base(container.container):
    def init(self):
        self.setting = addon.kodisetting(common.addon_id)
        self.__channels = None

    @property
    def validate(self):
        return self.setting.getbool("validate")
    
    @property
    def pvr(self):
        return self.setting.getbool("pvr")
    
    @property
    def port(self):
        return self.setting.getint("port")

    @property
    def channels(self):
        if self.__channels is None:
            hay_chan = self.hay("chan")
            self.__channels = hay_chan.find(common.hay_chan).data
        if self.validate or not self.__channels.get("alives"):
            self.do_validate(hay_chan)
            self.validate = False
        return self.__channels

    @validate.setter
    def validate(self, value):
        self.setting.set("validate", value)
        
    @port.setter
    def port(self, val):
        self.setting.set("port", val)
        
    def healthcheck(self, url):
        http_range = "bytes=0-300000"
        http_timeout = 2
        url, headers = net.fromkodiurl(url)
        if not headers:
            headers = {}
        if "user-agent" not in [x.lower() for x in headers.keys()]:
            headers[u"User-agent"] = const.USERAGENT
        try:
            headers["Range"] = http_range
            response = self.download(url, headers=headers, timeout=2)
            if not response[:7] == "#EXTM3U":
                return "None m3u8 File: %s" % url
            m3u = m3u8.loads(response, url)
            if m3u.is_variant:
                headers.pop("Range")
                for playlist in m3u.playlists:
                    response = self.download(playlist.absolute_uri, method="HEAD", headers=headers,
                                             timeout=http_timeout)
                    if not response.status_code == 200:
                        headers["Range"] = http_range
                        response = self.download(playlist.absolute_uri, headers=headers,
                                                 timeout=http_timeout)
            elif not len(m3u.segments):
                return "Broken m3u8 File: %s" % url
        except Exception, e:
            return str(e)

    def do_validate(self, ccache):
        chans = list(tools.safeiter(liblivechannels.iterchannels()))
        channels = {"alives": []}
        ccache.burn()
        pg = gui.progress("Checking")
        pg.update(0, "Loading Channels")
        index = 0
        for chan in chans:
            if pg.iscanceled():
                break
            valid = False
            c = liblivechannels.loadchannel(chan, self.download)
            index += 1
            error = "No links"
            if c.checkerrors is not None:
                error = c.checkerrors()
                if error is None:
                    error = "UP"
                    channels["alives"].append([c.icon, c.title, c.index, c.categories])
                pg.update(100 * index / len(chans), c.title, error, c.index)
                continue
            for url in tools.safeiter(c.get()):
                error = self.healthcheck(url)
                if error is None:
                    channels["alives"].append([c.icon, c.title, c.index, c.categories])
                    valid = True
                    pg.update(100 * index / len(chans), c.title, "UP", c.index)
                    break
            if not valid:
                pg.update(100 * index / len(chans), c.title, error, c.index)
            if index == 200000:
                break
        ccache.throw("channels", channels)
        ccache.snapshot()
        pg.close()
