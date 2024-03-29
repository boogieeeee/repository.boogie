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
try:
    import unittest
    import test

    class testses(unittest.TestCase):
        def test_ses_link(self):
            test.testlink(self, itermedias("beinsport-1-live"), 1, "bein1", 0)

except ImportError:
    pass

from liblivechannels.chexts.scrapertools import normalize
from tinyxbmc import tools
from tinyxbmc import net
from tinyxbmc import mediaurl
from six.moves.urllib import parse
import json
import base64

import htmlement

domain = "https://www.sestv3.pw/"

namemap = {"sinema17": "Bein Box Office 1",
           "sinema16": "Dizi TV",
           "sinema15": "Sinema TV 1001",
           "sinema14": "Sinema TV Aksiyon",
           "sinema13": "Sinema TV Aile",
           "sinema19": u"Bein Movies Turk",
           "nickeledeon": "Nickelodeon"
           }


def itermedias(chid, chids=None, adaptive=True):
    if not chids:
        chids = [chid]
    for chid in chids:
        url = domain + chid
        up = parse.urlparse(url)
        chid = up.path.split("/")[-1]
        subpage = htmlement.fromstring(net.http(url, referer=domain))
        embedlink = subpage.find(".//iframe").get("src")
        embedpage = htmlement.fromstring(net.http(embedlink, referer=url))
        script = embedpage.find(".//script[@id='v']")
        jsurl = "%s://%s/embed/%s" % (up.scheme, up.netloc, chid)
        data = {"e": 1, "id": int(script.get("data-i"))}
        scode = net.http(jsurl, referer=jsurl,
                         data=data, headers={"x-requested-with": "XMLHttpRequest",
                                             "origin": domain[:-1],
                                             "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                             "accept-encoding": "gzip, deflate, br",
                                             "accept-language": "en-US,en;q=0.9",
                                             "accept": "*/*",
                                             "sec-ch-ua-platform": "Linux",
                                             "origin": "https://www.sestv3.pw",
                                             "sec-fetch-site": "same-origin",
                                             "sec-fetch-mode": "cors",
                                             "sec-fetch-dest": "empty",
                                             "Cookie": "pop_2=1; pop_1=1; pop_4=1",
                                             "thief": "boogiepop@gmx.com ulas bana"},
                         method="POST")
        url = None
        scode = scode.replace("-", "+")
        scode = scode.replace("_", "/")
        scode = scode[::-1]
        for suffix in ["", "=", "=="]:
            try:
                url = base64.b64decode(scode + suffix)
                break
            except Exception:
                continue
        if url:
            url = url.decode()
            if "thief" not in url:
                yield mediaurl.hlsurl(url, headers={"referer": domain}, adaptive=adaptive)


def iterpage(xpage):
    for a in xpage.iterfind(".//div[@class='content container']/div/div/ul/li/a"):
        href = net.absurl(a.get("href").split("#")[0], domain)
        chname = tools.elementsrc(a).lower().strip()
        if "xxx" in chname.lower():
            continue
        normname = normalize(chname)
        if normname in namemap:
            chname = namemap[normname]
        icon = a.find(".//img")
        if icon is not None:
            icon = net.absurl(icon.get("src"), domain)
        _meta = json.dumps([href, chname, icon])
        yield href, chname, icon


def iteratechannels():
    xpage = htmlement.fromstring(net.http(domain))
    for ch in iterpage(xpage):
        yield ch
    pagination = xpage.findall(".//ul[@id='sayfalama']/.//a")
    lastpage = pagination[-1].get("href").split("/")[-1]
    for i in range(2, int(lastpage) + 1):
        xpage = htmlement.fromstring(net.http(domain + "/p/%s" % i))
        for ch in iterpage(xpage):
            yield ch
