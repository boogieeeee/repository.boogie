'''
Created on Aug 2, 2021

@author: boogie
'''
try:
    import unittest
    import test

    class testcanli(unittest.TestCase):
        def test_canli_link(self):
            test.testlink(self, itermedias("show-tv"), 1, "tv8", 0)

except ImportError:
    pass

from tinyxbmc import net
from tinyxbmc import mediaurl
import re


dom = "canlitv.center"
domain = "https://" + dom


def itermedias(ctvcid, ctvcids=None):
    if not ctvcids:
        ctvcids = [ctvcid]
    for ctvcid in ctvcids:
        u = domain + "/" + ctvcid
        srcroot = net.http(u, referer=domain)
        yayin = re.search(r"embedUrl(?:\'|\")\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")", srcroot).group(1)
        yield mediaurl.HlsUrl(yayin, headers={"referer": u}, adaptive=True, ffmpegdirect=False)
