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
import re
import htmlement
import json
from tinyxbmc import net
from tinyxbmc import const


dom = "https://soccerstreamslive.co"
streamdom = "https://cloudstreams.org"


class lfs(vods.movieextension):
    usedirect = True
    useaddonplayers = False
    uselinkplayers = False
    dropboxtoken = const.DB_TOKEN

    info = {"title": "LFS"
            }
    art = {}

    def getmovies(self, cat=None):
        for i in range(1, 30 + 1):
            chname = "Channel"
            self.additem("%s (#%s)" % (chname, i), i)

    def geturls(self, streamid):
        u = "%s/hdl%s.html" % (dom, streamid)
        iframeu = htmlement.fromstring(net.http(u)).find(".//iframe").get("src")
        iframe = net.http(iframeu, referer=u)
        fid = re.search("fid\s*?\=\*?(?:\'|\")(.+?)(?:\'|\")", iframe).group(1)
        cloud = net.http("%s/cloud.php?player=desktop&live=%s" % (streamdom, fid))
        url = re.search('return\((\[.+?\])', cloud).group(1)
        url = "".join(json.loads(url))
        yield net.hlsurl(url, headers={"Referer": streamdom}, adaptive=True)
