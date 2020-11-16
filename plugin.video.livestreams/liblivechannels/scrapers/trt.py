# -*- encoding: utf-8 -*-
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


class trt1(scraper):
    title = u"TRT 1"
    icon = "https://www.trt1.com.tr/public/logo/d60ab555-f948-464a-a139-df5410d2a7b5/trt1_logo.png"
    categories = [u"Türkçe", u"Realiti"]
    ushlsproxy = False

    def get(self):
        yield "https://tv-trt1.live.trt.com.tr/master.m3u8"
