'''
Created on Aug 2, 2021

@author: boogie
'''
try:
    import unittest
    import test

    class testcanli(unittest.TestCase):
        def test_canli_link(self):
            test.testlink(self, itermedias("tv8-izle-hd-canli"), 1, "tv8", 0)

except ImportError:
    pass

from tinyxbmc import net
from tinyxbmc import mediaurl
import htmlement
import re
import base64


dom = "canlitv.center"
domain = "https://" + dom

rgxlink = "yayin[a-zA-Z0-9]+[\s\t]*?\=[\s\t]*?(?:\"|\')(.*?)(?:\"|\')"


def findmedias(src, links, baseaddr):
    found = False
    media = re.search("file[\s\t]*?\:[\s\t]*?atob\((?:\"|\')(.+?)(?:\"|\')\)", src)
    if media:
        link = base64.b64decode(media.group(1)).decode()
        links.append(mediaurl.hlsurl(link, headers={"referer": domain}, adaptive=False, ffmpegdirect=False))
        found = True
    else:
        for link in re.findall(rgxlink, src):
            if "anahtar" in link:
                link = net.absurl(link, baseaddr)
                links.append(mediaurl.hlsurl(link, headers={"referer": domain}, adaptive=False, ffmpegdirect=False))
                found = True
                break
    return found

def itersubpages(src):
    found = False
    for iframe2 in re.findall('iframe.*?src=\\\\?"(.+?)\\\\"', src):
        found = True
        link = iframe2.replace("\\", "").replace("\"+host_name+\"", dom)
        yield link
    if not found:
        for script in re.findall('script src=\\\\?"(.+?)"', src):
            found = True
            yield script.replace("\\", "")
    if not found:
        iframe1 = htmlement.fromstring(src).find(".//iframe")
        if iframe1 is not None:
            yield iframe1.get("src")


def itermedias(ctvcid, ctvcids=None):
    if not ctvcids:
        ctvcids = [ctvcid]
    for ctvcid in ctvcids:
        links = []
        u = domain + "/" + ctvcid
        srcroot = net.http(u, referer=domain)
        for subpage1 in itersubpages(srcroot):
            sub1src = net.http(subpage1, referer=domain)
            found = findmedias(sub1src, links, subpage1)
            if not found:
                for subpage2 in itersubpages(sub1src):
                    sub2src = net.http(subpage2, referer=domain)
                    found = findmedias(sub2src, links, subpage2)
                    if not found:
                        for subpage3 in itersubpages(sub2src):
                            sub3src = net.http(subpage3, referer=domain)
                            findmedias(sub3src, links, subpage3)
        for link in links:
            yield link
