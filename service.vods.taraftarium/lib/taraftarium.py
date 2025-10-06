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
from tinyxbmc.const import DB_TOKEN
import libtaraftarium


class taraftarium(vods.movieextension):
    dropboxtoken = DB_TOKEN
    uselinkplayers = False
    useaddonplayers = False

    info = {"title": "Taraftarium"}

    def getmovies(self):
        for chlink, chname in libtaraftarium.iteratechannels():
            self.additem(chname, chlink)

    def geturls(self, chlink):
        for media in libtaraftarium.geturls(chlink):
            yield media
