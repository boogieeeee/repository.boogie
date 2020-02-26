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
from tinyxbmc import extension

import time

import liblivechannels
from liblivechannels import common

from thirdparty import m3u8

_chancls = {}
_chanins = {}


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
    def lastupdate(self):
        return self.setting.getint("lastupdate")
    
    @property
    def port(self):
        return self.setting.getint("port")
    
    @property
    def resolve_mode(self):
        modes = {"First highest quality variant in first alive stream": 0,
                 "First alive stream with all variants": 1,
                 "All streams with all variants redundantly": 2
                 }
        return modes[self.setting.getstr("pvr_resolve_mode")]

    @property
    def channels(self):
        self.__channels = self.hay("chan").find(common.hay_chan).data
        return self.__channels
    
    @lastupdate.setter
    def lastupdate(self, value):
        self.setting.set("lastupdate", value)

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
            response = self.download(url, headers=headers, timeout=2, cache=None)
            if not response[:7] == "#EXTM3U":
                return "None m3u8 File: %s" % url
            m3u = m3u8.loads(response, url)
            if m3u.is_variant:
                headers.pop("Range")
                for playlist in m3u.playlists:
                    response = self.download(playlist.absolute_uri, method="HEAD", headers=headers,
                                             timeout=http_timeout,cache=None)
                    if not response.status_code == 200:
                        headers["Range"] = http_range
                        response = self.download(playlist.absolute_uri, headers=headers,
                                                 timeout=http_timeout, cache=None)
            elif not len(m3u.segments):
                return "Broken m3u8 File: %s" % url
        except Exception, e:
            return str(e)

    def do_validate(self, ccache, silent=False, is_closed=None):
        chans = list(tools.safeiter(self.iterchannels()))
        channels = {"alives": []}
        if not silent:
            pg = gui.progress("Checking")
            pg.update(0, "Loading Channels")
        index = 0
        for chan in chans:
            if is_closed or not silent and pg.iscanceled():
                break
            valid = False
            c = self.loadchannel(chan)
            index += 1
            error = "No links"
            if c.checkerrors is not None:
                error = c.checkerrors()
                if error is None:
                    error = "UP"
                    channels["alives"].append([c.icon, c.title, c.index, c.categories])
                if not silent:
                    pg.update(100 * index / len(chans), c.title, error, c.index)
                continue
            for url in tools.safeiter(c.get()):
                error = self.healthcheck(url)
                if error is None:
                    channels["alives"].append([c.icon, c.title, c.index, c.categories])
                    valid = True
                    if not silent:
                        pg.update(100 * index / len(chans), c.title, "UP", c.index)
                    break
            if not valid and not silent:
                pg.update(100 * index / len(chans), c.title, error, c.index)
            if index == 200000:
                break
        ccache.burn()
        ccache.throw("channels", channels)
        ccache.snapshot()
        self.lastupdate = int(time.time())
        if not silent:
            pg.close()
    
    def getchannel(self, channelid):
        for chan in self.iterchannels():
            if chan.index in _chancls:
                return _chancls[chan.index]
            elif chan.index == channelid:
                _chancls[chan.index] = cls
                return cls
    
    def iterchannels(self, *cats):
        def _iterobjs():
            for mod, cls in extension.getobjects(common.dpath, parents=[liblivechannels.scraper]):
                if cls.subchannel:
                    continue
                if not cls.index:
                    cls.index = "%s:%s:" % (mod.__name__, cls.__name__)
                yield cls
            for mod, cls in extension.getobjects(common.dpath, parents=[liblivechannels.scrapers]):
                cls_ob = cls(self.download)
                for cls_sub in cls_ob.iteratechannels():
                    if not cls_sub.index:
                        cls_sub.index = "%s:%s:%s" % (mod.__name__, cls.__name__, cls_sub.__name__)
                    yield cls_sub
    
        for cls in _iterobjs():
            found = False
            for c in cats:
                if c in cls.categories:
                    found = True
                    break
            if not found and len(cats):
                continue
            if cls.index not in _chancls:
                _chancls[cls.index] = cls
            yield cls
        
    def loadchannel(self, chan):
        try:
            iscls = issubclass(chan, liblivechannels.scraper)
        except Exception:
            iscls = False
        if iscls:
            chanid = chan.index
            if chanid not in _chanins:
                _chanins[chanid] = chan(self.download)
        else:
            chanid = chan
            if chanid not in _chanins:
                m, c, subc = chanid.split(":")
                if subc == "":
                    for mod, cls in extension.getobjects(common.dpath, m, c, parents=[liblivechannels.scraper]):
                        if cls.subchannel:
                            continue
                        cls.index = "%s:%s:" % (mod.__name__, cls.__name__)
                        if chanid == cls.index:
                            _chanins[chanid] = cls(self.download)
                            break
                else:
                    for mod, cls in extension.getobjects(common.dpath, m, c, parents=[liblivechannels.scrapers]):
                        if cls.__name__ == c and mod.__name__ == m:
                            subcls = cls(self.download)._getchannel(subc)
                            subcls.index = "%s:%s:%s" % (mod.__name__, cls.__name__, subcls.__name__)
                            _chanins[chanid] = subcls(self.download)
        return _chanins[chanid]
    
    def getcategories(self):
        cats = []
        for chan in self.iterchannels():
            if isinstance(chan.categories, (list, tuple)):
                for c in chan.categories:
                    if c not in cats:
                        cats.append(c)
                        yield c
