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
from tinyxbmc import net
import liblfs
import chanmeta


MAXCHAN = 30


class lfs(vods.movieextension):
    usedirect = True
    useaddonplayers = False
    uselinkplayers = False
    dropboxtoken = const.DB_TOKEN

    info = {"title": "LFS"
            }
    art = {}

    def getmovies(self, cat=None):
        for i in range(1, MAXCHAN + 1):
            chname = chanmeta.chnames.get(i) or "Channel (#%s)" % i
            if self.setting.getbool("verify"):
                url = liblfs.get(i)
                if url:
                    resp = net.http(url.url, headers=url.headers, method="HEAD", cache=None)
                    if resp.status_code == 200:
                        self.additem(chname, url)
            else:
                self.additem(chname, i)

    def geturls(self, vid):
        if self.setting.getbool("verify"):
            yield vid
        else:
            yield liblfs.get(vid)