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
from tinyxbmc import extension

import time
import traceback

import liblivechannels
from liblivechannels import common
from liblivechannels import config
from liblivechannels import epg

from thirdparty import m3u8

_chancls = {}
_chanins = {}


class Base(container.container):
    def init(self):
        self.config = config.config()

    def proxy_get(self, url, headers, method="GET"):
        for retry in range(3):
            if "user-agent" not in [x.lower() for x in headers.keys()]:
                headers[u"User-agent"] = const.USERAGENT
            try:
                resp = self.download(url, headers=headers, text=False,
                                     timeout=common.query_timeout, cache=None, method=method)
                if resp.status_code not in [200, 206]:
                    if retry == 2:
                        return resp
                    else:
                        continue
                else:
                    return resp
            except Exception, e:
                if retry == 2:
                    return e

    def healthcheck(self, url, headers=None):
        if headers is None:
            url, headers = net.fromkodiurl(url)
        if not headers:
            headers = {}
        response = self.proxy_get(url, headers)
        if response is None or isinstance(response, Exception) or not response.content[:7] == "#EXTM3U":
            return "M3U8 File does not have correct header"
        m3u = m3u8.loads(response.content, url)
        if m3u.is_variant:
            for playlist in m3u.playlists:
                response = self.proxy_get(playlist.absolute_uri, headers, "HEAD")
                if response is None or isinstance(response, Exception) or response.status_code not in [200, 206]:
                    response = self.proxy_get(playlist.absolute_uri, headers)
                    if response is not None and not isinstance(response, Exception) and response.status_code in [200, 206]:
                        return  # Successfull GET
                else:  # Successfull HEAD
                    return
            return "M3U8 File has no available variant"
        elif not len(m3u.segments):
            return "M3U8 File has no available segment"

    def do_validate(self, silent=False, is_closed=None):
        if self.config.update_running:
            if not silent:
                gui.ok("Update Running", "A current update of channels is in progress in background")
                self.config.validate = False
            return
        self.config.update_running = True
        chans = list(tools.safeiter(self.iterchannels()))
        channels = []
        if not silent:
            pg = gui.progress("Checking")
            pg.update(0, "Loading Channels")
        index = 0
        for chan in chans:
            if is_closed or not silent and pg.iscanceled():
                break
            valid = False
            c = self.loadchannel(chan)
            if not c:
                continue
            index += 1
            error = "No links"
            if c.checkerrors is not None:
                error = c.checkerrors()
                if error is None:
                    error = "UP"
                else:
                    c.categories = ["Broken"]
                channels.append([c.icon, c.title, c.index, c.categories])
                if not silent:
                    pg.update(100 * index / len(chans), c.title, error, c.index)
                continue
            for url in tools.safeiter(c.get()):
                error = self.healthcheck(url)
                if error is None:
                    valid = True
                    if not silent:
                        pg.update(100 * index / len(chans), c.title, "UP", c.index)
                    break
            if not valid:
                c.categories = ["Broken"]
                if not silent:
                    pg.update(100 * index / len(chans), c.title, error, c.index)
            channels.append([c.icon, c.title, c.index, c.categories])
            if index == 200000:
                break
        self.config.channels = channels
        self.config.lastupdate = int(time.time())
        self.config.update_running = False
        self.config.update_pvr = True
        epg.write(self).start()
        if not silent:
            pg.close()

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
                for cls_sub in tools.safeiter(cls_ob.iteratechannels()):
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
                            try:
                                subcls = cls(self.download)._getchannel(subc)
                            except Exception:
                                print traceback.format_exc()
                                continue
                            subcls.index = "%s:%s:%s" % (mod.__name__, cls.__name__, subcls.__name__)
                            _chanins[chanid] = subcls(self.download)
        return _chanins.get(chanid)
