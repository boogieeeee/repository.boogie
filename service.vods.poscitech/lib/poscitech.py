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
    GNU General Public License for more detail```    s.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import vods

from tinyxbmc import const
import libdaddy


class poscitech(vods.movieextension):
    usedirect = True
    useaddonplayers = False
    uselinkplayers = False
    dropboxtoken = const.DB_TOKEN

    info = {"title": "DaddyLive"
            }
    art = {"icon": "https://i.imgur.com/8EL6mr3.png",
           "thumb": "https://i.imgur.com/8EL6mr3.png",
           "poster": "https://i.imgur.com/8EL6mr3.png"
           }

    def getcategories(self):
        for evdate, sport, title, channels in sorted(libdaddy.getevents()):
            title = "%02d.%02d %02d:%02d | %s | %s" % (evdate.day, evdate.month, evdate.hour, evdate.minute,
                                                    sport, title)
            self.additem(title, channels)

    def getmovies(self, cat=None):
        if cat:
            for ctxt, cnum in cat:
                self.additem(ctxt, cnum)
        else:
            chnames = libdaddy.getchmeta(numbyname=True)
            for i in range(1, 200 + 1):
                chname = chnames.get(i, "Channel")
                self.additem("%s (#%s)" % (chname, i), i)

    def geturls(self, streamid):
        yield libdaddy.geturl(streamid)
