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


class scraper(object):
    title = "Unknown Channel"
    icon = "DefaultFolder.png"
    categories = []
    index = None
    checkerrors = None
    subchannel = False

    def __init__(self, download):
        self.download = download

    def config(self):
        pass

    def get(self):
        pass
    
class scrapers(object):
    def __init__(self, download):
        self.download = download
        
    def makechannel(self, cid, base, **kwargs):
        return type("ch_" + cid.encode("hex"), (base,), kwargs)

    def _getchannel(self, cid):
        return self.getchannel(cid[3:].decode("hex"))

    def iteratechannels(self):
        yield

    def getchannel(self, cid):
        pass
