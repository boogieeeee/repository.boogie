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
import os
import datetime
from tinyxbmc import tools
from tinyxbmc.tools import tz_utc, tz_local

utc_tz = tz_utc()
loc_tz = tz_local()


class programme(object):
    def __init__(self, title, start, end, airdate=None, desc=None, categories=None, subtitle=None,
                 episode=None, directors=None, writers=None, actors=None, icon=None):
        self.__dateformat1 = "%Y%m%d%H%M%S %z"
        self.title = title
        self._start = start
        self._end = end
        self._airdate = airdate
        self.desc = desc
        if categories:
            self.categories = categories
        else:
            self.categories = []
        self.subtitle = subtitle
        self.episode = episode
        if directors:
            self.directors = directors
        else:
            self.directors = []
        if writers:
            self.writers = writers
        else:
            self.writers = []
        if actors:
            self.actors = actors
        else:
            self.actors = []
        self.icon = icon

    @property
    def start(self):
        if self._start:
            return self._start.astimezone(loc_tz).strftime(self.__dateformat1)

    @property
    def end(self):
        if self._end:
            return self._end.astimezone(loc_tz).strftime(self.__dateformat1)

    @property
    def airdate(self):
        pass


class scraper(object):
    title = "Unknown Channel"
    icon = "DefaultFolder.png"
    categories = []
    index = None
    checkerrors = None
    subchannel = False
    usehlsproxy  = True

    def __init__(self, download):
        self.download = download
        self.__programmes = []

    def config(self):
        pass

    def get(self):
        pass

    def iterprogrammes(self):
        raise StopIteration
        yield


class scrapers(object):
    def __init__(self, download):
        self.download = download

    def makechannel(self, cid, base, **kwargs):
        if "icon" in kwargs and not isinstance(kwargs["icon"], (str, unicode)):
            kwargs.pop("icon")
        return type("ch_" + cid.encode("hex"), (base,), kwargs)

    def _getchannel(self, cid):
        return self.getchannel(cid[3:].decode("hex"))

    def iteratechannels(self):
        yield scraper

    def getchannel(self, cid):
        pass
