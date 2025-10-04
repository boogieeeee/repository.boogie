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
from tinyxbmc import const
from tinyxbmc.tools import tz_utc, tz_local

utc_tz = tz_utc()
loc_tz = tz_local()


class programme(object):
    def __init__(self, title, start, end, airdate=None, desc=None, categories=None, subtitle=None,
                 episode=None, directors=None, writers=None, actors=None, icon=None):
        self.__dateformat1 = "%Y%m%d%H%M%S %z"
        self.title = title
        self.start = start.astimezone(loc_tz).strftime(self.__dateformat1)
        self.end = end.astimezone(loc_tz).strftime(self.__dateformat1)
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
    def airdate(self):
        pass


class scraper(object):
    title = "Unknown Channel"
    icon = const.DEFAULT_FOLDER
    categories = []
    index = None
    checkerrors = None
    subchannel = False
    pvrinputstream = None

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
