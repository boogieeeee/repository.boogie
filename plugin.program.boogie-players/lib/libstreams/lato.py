'''
Created on Oct 7, 2025

@author: boogie
'''
from streams import StreamsBase, Test
from tinyxbmc import net
from tinyxbmc import mediaurl

from urllib import parse

import re
import json
import unittest


class Lato(StreamsBase):
    regex = r"lato\."

    def resolve(self, url, headers):
        up = parse.urlparse(url)
        apiurl = f"{up.scheme}://{up.netloc}/api/player.php?{up.query}"
        src = net.http(apiurl, referer=url, json=True)
        vidurl = src["url"]
        vidpage = net.http(vidurl, referer=url)
        hlsurl = re.search(r"var\s*?src\s*?=\s*?(?:\'|\")(.+?)(?:\'|\")", vidpage).group(1)
        up = parse.urlparse(vidurl)
        origin = f"{up.scheme}://{up.netloc}"
        referer = origin + "/"
        yield mediaurl.HlsUrl(hlsurl, headers={"origin": origin,
                                               "referer": referer})


class TestLink(unittest.TestCase, Test):
    link = "https://lato.sx/ch.php?id=1"
