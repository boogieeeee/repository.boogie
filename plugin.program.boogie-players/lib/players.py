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

from tinyxbmc import addon

from vods import linkplayerextension
from vods import addonplayerextension

from libplayer import getconfig

import ghub
import urllib
import sys


class streamlink(linkplayerextension):
    title = "StreamLink Link Extension"

    def init(self):
        self.title = "StreamLink Link Resolver"
        uname, branch, commit = getconfig("sl")
        update = 24 * 30
        ghub.load("minrk", "backports.shutil_which", None, None, [], update)
        ghub.load("gweis", "isodate", None, None, ["src"], update)
        ghub.load("beardypig", "script.module.streamlink.crypto", "master", None, ["streamlink.crypto", "src"], update)
        ghub.load("beardypig", "script.module.pycountry", "master", None, ["pycountry", "src"], update)
        ghub.load("minrk", "backports.shutil_which", None, None, [], update)
        ghub.load("ambv", "singledispatch", None, None, [], update)
        ghub.load("agronholm", "pythonfutures", None, None, [], update)
        ghub.load(uname, "streamlink", branch, commit, ["src"], update)
        import streamlink
        self.sl = streamlink

    def geturls(self, link, headers=None):
        try:
            streams = self.sl.streams(link)
        except StopIteration:  # bug in sl
            yield


class plexus(addonplayerextension):
    title = "PlexusAddon Extension"

    def geturls(self, link, headers=None):
        if addon.has_addon('program.plexus'):
            mode = 0
            if link.lower().startswith("acestream://"):
                mode = 1
            elif link.lower().startswith("sop://"):
                mode = 2
            if not mode:
                yield
            query = {"url": link, "mode": mode, "name": "Acestream"}
            yield "plugin://program.plexus/?" + urllib.urlencode(query)


class elementum(addonplayerextension):
    title = "Elementum Extension"

    def geturls(self, link, headers=None):
        if not addon.has_addon('plugin.video.elementum'):
            yield
        if link.lower().startswith("magnet:?") or link.lower().endswith(".torrent"):
            yield "plugin://plugin.video.elementum/play?uri=%s" % link
