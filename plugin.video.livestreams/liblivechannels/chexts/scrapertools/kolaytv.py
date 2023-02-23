'''
Created on Jun 6, 2021

@author: boogie
'''
try:
    import unittest
    import test

    class testkolay(unittest.TestCase):
        def test_kolay_link(self):
            test.testlink(self, itermedias("/tv8-canli-yayinlar"), 1, "tv8", 0)

except ImportError:
    pass

from tinyxbmc import net
from tinyxbmc import mediaurl
from liblivechannels import unwise

import htmlement
import re
import traceback

domain = "https://www.donmaztv.com"

rgx = "}\((?:\"|\')(.*?)(?:\"|\')\s*?\,\s*?(?:\"|\')(.*?)(?:\"|\')\s*?\,\s*?(?:\"|\')(.*?)(?:\"|\')\s*?\,\s*?(?:\"|\')(.*?)(?:\"|\')\)"
rgx2 = "file\s*?\:\s*?(?:\"|\')(.+?)(?:\"|\')"


def itermedias(chlink, chlinks=None):
    links = []
    if not chlinks:
        chlinks = [chlink]
    for chlink in chlinks:
        url = domain + chlink
        page = htmlement.fromstring(net.http(url, referer=domain))
        iurl = page.find(".//iframe").get("src")
        ipage = net.http(iurl, referer=url)
        iurl2 = re.search('src="(.+?)".+iframe', ipage).group(1)
        iurl2 = iurl2.replace("'+ulke+'", "DE")
        ipage = net.http(iurl2, referer=iurl)
        try:
            wise = unwise.unwise(*re.findall(rgx, ipage)[0])
            wise = unwise.unwise(*re.findall(rgx, wise)[0])
            wise = unwise.unwise(*re.findall(rgx, wise)[1])
            media = re.search(rgx2, wise.replace("\\", "")).group(1)
            links.append(mediaurl.hlsurl(media, headers={"referer": domain + "/"}, adaptive=False, ffmpegdirect=False))
        except Exception:
            print(traceback.format_exc())
    links.reverse()
    for link in links:
        yield link
