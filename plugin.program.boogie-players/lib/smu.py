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

from tinyxbmc import tools
from tinyxbmc import hay
from tinyxbmc import net
from tinyxbmc import const
from tinyxbmc import mediaurl

from vods import linkplayerextension

from bplay import getconfig

import ghub
import os
import re
import json

PATCHVER = "versioncommit_v4"


def patchsmu(smudir):
    smudir = os.path.join(smudir, "script.module.resolveurl")
    with hay.stack("smupatch") as smuhay:
        smupatch = smuhay.find("smupatch").data
        with open(os.path.join(smudir, "..", "..", "ResolveURL.json")) as vf:
            versioncommit = json.load(vf)
        versioncommit = versioncommit.get("latest")

        if smupatch.get(PATCHVER) == versioncommit:
            return

        # first remove xbmcaddon referenced to script.module.urlresolver
        files = [(["lib", "resolveurl", "lib", "log_utils.py"], 1),
                 (["lib", "resolveurl", "lib", "kodi.py"], 1),
                 (["lib", "resolveurl", "lib", "CustomProgressDialog.py"], 1),
                 (["lib", "resolveurl", "common.py"], 2),
                 (["lib", "resolveurl", "lib", "kodi.py"], 3),
                 (["lib", "resolveurl", "lib", "helpers.py"], 4)
                 ]
        for fpaths, patchtype in files:
            fpath = os.path.join(smudir, *fpaths)
            with open(fpath, "r") as f:
                contents = f.read()
            if patchtype == 1:
                pattern = r"script\.module\.resolveurl"
                sub = "plugin.program.boogie-players"
            elif patchtype == 2:
                pattern = r"settings_file \= os\.path\.join\(addon_path, 'resources', 'settings.xml'\)"
                sub = "settings_file = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.xml')"
            elif patchtype == 3:
                pattern = r"xbmcaddon.Addon\(\)"
                sub = "xbmcaddon.Addon('plugin.program.boogie-players')"
            elif patchtype == 4:
                pattern = r"auto_pick=None"
                sub = "auto_pick=True"
            if re.search(pattern, contents):
                with open(fpath, "w") as f:
                    f.write(re.sub(pattern, sub, contents))

            smupatch[PATCHVER] = versioncommit
            smuhay.throw("smupatch", smupatch)
            tools.builtin("UpdateLocalAddons()")
            # gui.ok("URL Resolvers", "SMU has just been updated\nSome changes will be active on the next run")


class smu(linkplayerextension):
    dropboxtoken = const.DB_TOKEN

    def init(self):
        uname, branch, commit = getconfig("smu")
        ghub.load("romanvm", "kodi.six", "master", None, ["script.module.kodi-six", "libs"])
        patchsmu(ghub.load(uname, "ResolveURL", branch, commit, ["script.module.resolveurl", "lib"]))
        from resolveurl import hmf
        self.hmf = hmf.HostedMediaFile

    def geturls(self, link, headers=None):
        hmf = self.hmf(link, include_universal=True, include_disabled=True, include_popups=False)
        resolved = hmf.resolve()
        if resolved:
            yield mediaurl.LinkUrl(*net.fromkodiurl(resolved))
