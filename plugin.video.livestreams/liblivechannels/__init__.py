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
from tinyxbmc import extension
import os

dpath = os.path.join(os.path.dirname(__file__), "scrapers")
_chancls = {}
_chanins = {}


class scraper(object):
    title = "Unknown Channel"
    icon = "DefaultFolder.png"
    categories = []
    index = None
    checkerrors = None

    def __init__(self, download):
        self.download = download

    def get(self):
        pass


def getchannel(channelid):
    for chan in iterchannels():
        if chan.index in _chancls:
            return _chancls[chan.index]
        elif chan.index == channelid:
            _chancls[chan.index] = cls
            return cls


def iterchannels(*cats):
    for mod, cls in extension.getobjects(dpath, parents=[scraper]):
        found = False
        for c in cats:
            if c in cls.categories:
                found = True
                break
        if not found and len(cats):
            continue
        if not cls.index:
            cls.index = "%s:%s" % (mod.__name__, cls.__name__)
        if cls.index not in _chancls:
            _chancls[cls.index] = cls
        yield cls


def loadchannel(chan, download):
    try:
        iscls = issubclass(chan, scraper)
    except Exception:
        iscls = False
    if iscls:
        chanid = chan.index
        if chanid not in _chanins:
            _chanins[chanid] = chan(download)
    else:
        chanid = chan
        if chanid not in _chanins:
            m, c = chanid.split(":")
            for mod, cls in extension.getobjects(dpath, m, c, parents=[scraper]):
                cls.index = "%s:%s" % (mod.__name__, cls.__name__)
                if chanid == cls.index:
                    _chanins[chanid] = cls(download)
                    break
    return _chanins[chanid]


def getcategories():
    cats = []
    for chan in iterchannels():
        if isinstance(chan.categories, (list, tuple)):
            for c in chan.categories:
                if c not in cats:
                    cats.append(c)
                    yield c
