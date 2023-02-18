'''
Created on Aug 2, 2021

@author: boogie
'''
try:
    import unittest
    import test

    class testcanli(unittest.TestCase):
        def test_canli_link(self):
            test.testlink(self, itermedias("tv-8-canli/2"), 1, "tv8", 0)

except ImportError:
    pass

from tinyxbmc import net
from tinyxbmc import mediaurl
import htmlement
import re
import base64


dom = "canlitv.center"
domain = "https://" + dom

#rgxkey = "verianahtar[\s\t]*?\=[\s\t]*?(?:\"|\')(.+?)(?:\"|\')"
rgxlink = "yayin[a-zA-Z0-9]+[\s\t]*?\=[\s\t]*?(?:\"|\')(.*?)(?:\"|\')"


def itermedias(ctvcid, ctvcids=None):
    if not ctvcids:
        ctvcids = [ctvcid]
    for ctvcid in ctvcids:
        links = []
        u = domain + "/" + ctvcid
        iframe1 = htmlement.fromstring(net.http(u, referer=domain)).find(".//iframe").get("src")
        iframe2 = htmlement.fromstring(net.http(iframe1, referer=u)).find(".//iframe").get("src")
        src = net.http(iframe2, referer=iframe1)
        media = re.search("file[\s\t]*?\:[\s\t]*?atob\((?:\"|\')(.+?)(?:\"|\')\)", src)
        if media:
            link = base64.b64decode(media.group(1)).decode()
            links.append(mediaurl.hlsurl(link, headers={"referer": domain}))
        else:
            for script in re.findall('script src=\\\\"(.+?)"', src):
                ssrc = script.replace("\\", "")
                scriptsrc = net.http(ssrc, referer=domain)
                #key = re.search(rgxkey, scriptsrc)
                #if key:
                for link in re.findall(rgxlink, scriptsrc):
                    if "anahtar" in link:
                        link = net.absurl(link, ssrc)
                        #links.append(net.hlsurl(link + key.group(1), headers={"referer": domain}))
                        links.append(mediaurl.hlsurl(link, headers={"referer": domain}))
        for link in links:
            yield link
