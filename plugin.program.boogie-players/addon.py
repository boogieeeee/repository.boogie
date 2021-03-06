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

from tinyxbmc import container
from tinyxbmc import addon

addons = (("Plexus", "program.plexus", "Plays Acestream and Sopcast"),
          ("Quasar", "plugin.video.quasar", "Plays torrents"),
          )


class navi(container.container):

    def index(self):
        for [adn, aid, desc] in addons:
            if not addon.has_addon(aid):
                install = "[COLOR red][not installed][/COLOR]"
            else:
                install = "[COLOR green][installed][/COLOR]"
            name = "%s %s - %s" % (install, adn, desc)
            self.item(name).call()


navi()
