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

import libflix


class base(object):
    ismovie = False
    usedirect = False
    useaddonplayers = False

    def getcategories(self):
        libflix.getcategories(self)

    def geturls(self, url):
        for u in libflix.geturls(self, url):
            yield u


class cartoonhdmovies(base, vods.movieextension):
    info = {"title": "Flixanity Movies"}
    ismovie = True

    def init(self):
        super(cartoonhdmovies, self).init()
        self.sort = self.setting.getstr("sortm").lower().replace(" ", "-")

    def getmovies(self, cat=None):
        self.setnextpage(libflix.srapegrid(self, cat))

    def cachemovies(self, url):
        return libflix.scrapeinfo(self, url)

    def searchmovies(self, keyword):
        return libflix.search(self, keyword)


class cartoonhdseries(base, vods.showextension):
    info = {"title": "Flixanity Series"}
    ismovie = False

    def init(self):
        super(cartoonhdseries, self).init()
        self.sort = self.setting.getstr("sorts").lower().replace(" ", "-")

    def getshows(self, cat=None):
        self.setnextpage(libflix.srapegrid(self, cat))

    def cacheshows(self, url):
        return libflix.scrapeinfo(self, url)

    def searchshows(self, keyword):
        return libflix.search(self, keyword)

    def getseasons(self, showargs=None):
        return libflix.getseasons(self, showargs)

    def getepisodes(self, showargs=None, seaargs=None):
        libflix.getepisodes(self, showargs, seaargs)

    def cacheepisodes(self, url):
        return libflix.cacheepisodes(self, url)
