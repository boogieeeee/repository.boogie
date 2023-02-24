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
from tinyxbmc import mediaurl

import time
import traceback
import socket
import urllib3

import liblivechannels
from liblivechannels import common
from liblivechannels import config
from liblivechannels import epg
from liblivechannels import pvr

from thirdparty import m3u8
import aceengine

_chancls = {}
_chanins = {}


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Base(container.container):
    iptvsimple = pvr.iptv

    def init(self):
        self.config = config.config()

    def isinvalidresponse(self, response):
        return response is None or isinstance(response, Exception) or response.status_code not in [200, 206]

    def http_retry(self, url, headers, method="GET"):
        _headers = headers.copy()
        for retry in range(3):
            if "user-agent" not in [x.lower() for x in _headers.keys()]:
                _headers[u"User-agent"] = const.USERAGENT
            try:
                resp = self.download(url, headers=_headers, text=False,
                                     timeout=common.query_timeout, stream=True,
                                     cache=None, method=method, verify=False)
                if resp.status_code not in [200, 206]:
                    if retry == 2:
                        return resp
                    else:
                        continue
                else:
                    return resp
            except Exception as e:
                if retry == 2:
                    return e

    def check_mpdurl(self, url):
        # DASH streams, most likely this block is partly broken since no channels provide DASH
        if not url.inputstream:
            if url.kodilurl:
                return "Inputstream.adaptive cant play encrypted streams", None, None
            else:
                return "Inputstream.adaptive not available", None, None
        if self.isinvalidresponse(self.http_retry(url.url, url.headers)):
            return "MPD url is inaccessable", None, None
        if url.lurl and False:
            if self.isinvalidresponse(self.http_retry(url.lurl, url.lheaders)):
                return "MPD license url is inaccessable", None, None
        return None, None, None

    def check_acestreamurl(self, url):
        response = self.http_retry(url.kodiurl, {})
        if self.isinvalidresponse(response):
            return "Broken Acestream URL", None, None
        return None, None, None
        #for _second in range(10):
            #stats = aceengine.stats(url)
            #if stats.get("status") == "dl":
            #    aceengine.stop(url)
            #    return None, None, None
            #time.sleep(1)

    def check_hlsurl(self, url, forceget=False):
        if isinstance(url, mediaurl.hlsurl):
            headers = url.headers
            u = url.url
        else:
            u, headers = net.fromkodiurl(url)
        if not headers:
            headers = {}
        manifest = self.http_retry(u, headers)
        if self.isinvalidresponse(manifest) or not manifest.content[:7].decode() == "#EXTM3U":
            return "M3U8 File does not have correct header", manifest, headers
        m3u = m3u8.loads(manifest.content.decode(), manifest.url)
        if m3u.is_variant:
            for playlist in m3u.playlists:
                if not forceget:
                    response = self.http_retry(playlist.absolute_uri, headers, "HEAD")
                else:
                    response = None
                if self.isinvalidresponse(response):
                    # HEAD may not be supported, do a get
                    response = self.http_retry(playlist.absolute_uri, headers)
                    if not self.isinvalidresponse(response) and response.content[:7].decode() == "#EXTM3U":
                        return None, manifest, headers  # Successfull GET
                else:
                    # Successfull HEAD
                    return None, manifest, headers
            return "M3U8 File has no available variant", manifest, headers
        elif not len(m3u.segments):
            return "M3U8 File has no available segment", manifest, headers
        else:
            return None, manifest, headers

    def healthcheck(self, url):
        # MPD url
        if isinstance(url, mediaurl.mpdurl):
            return self.check_mpdurl(url)
        # Acestream URLs
        if isinstance(url, mediaurl.acestreamurl):
            return self.check_acestreamurl(url)
        # HLS URLs
        return self.check_hlsurl(url)

    def checkinternet(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.config.internetaddress, 80))
            s.close()
            return True
        except Exception:
            return False

    def do_validate(self, background=False, is_closed=None):
        if self.config.update_running:
            return
        self.config.update_running = True
        chans = list(tools.safeiter(self.iterchannels()))
        channels = []
        pgname = "Updating Channels"
        if background:
            pg = gui.bgprogress(pgname)
        else:
            pg = gui.progress("Checking")
            pg.update(0, pgname)
        index = 0
        for chan in chans:
            if not self.checkinternet():
                gui.warn("No Connection", "Skipping Channel Update")
                self.config.lastupdate = int(time.time())
                self.config.validate = False
                self.config.update_running = False
                pg.close()
                return
            if is_closed or hasattr(pg, "iscanceled") and pg.iscanceled():
                self.config.update_running = False
                break
            c = self.loadchannel(chan)
            if not c:
                continue
            index += 1
            error = None
            found = False
            if c.checkerrors is not None:
                error = c.checkerrors()
            if error is None:
                for url in tools.safeiter(c.get()):
                    error, _resp, _header = self.healthcheck(url)
                    if error is None:
                        # at least one url is enough
                        found = True
                        break
            if not error and not found:
                error = "No playlist"
            if error is None:
                channels.append([c.icon, c.title, c.index, c.categories, url if isinstance(url, mediaurl.url) else None])
                error = "UP"
            pg.update(int(100 * index / len(chans)), "%s\n%s: %s" % (c.title, error, c.index))
            if index == 200000:
                break
        self.config.channels = channels
        epg.write(self, pg)
        self.config.lastupdate = int(time.time())
        self.config.update_running = False
        if self.config.validate:
            self.config.validate = False
        self.config.update_pvr = True
        pg.close()

    def iterchannels(self, *cats):
        def _iterobjs():
            for mod, cls in extension.getobjects(common.dpath, parents=[liblivechannels.scraper]):
                if cls.subchannel:
                    continue
                if not cls.index:
                    cls.index = "%s:%s:" % (mod.__name__, cls.__name__)
                yield cls

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
        return _chanins.get(chanid)
