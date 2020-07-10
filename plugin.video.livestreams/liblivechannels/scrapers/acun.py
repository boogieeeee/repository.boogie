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
from liblivechannels import scraper
import ecanli


class tv8(scraper):
    categories = ["Turkish", "Entertainment", "Turkey"]
    title = u"Tv 8"
    icon = "https://img.tv8.com.tr/s/template/v2/img/tv8-logo.png"

    def get(self):
        for media in ecanli.iterexternal(self.download, self.title):
            yield media
        yield "https://tv8.personamedia.tv/tv8hls?fmt=hls"
