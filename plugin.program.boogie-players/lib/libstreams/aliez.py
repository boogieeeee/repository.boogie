'''
Created on Oct 7, 2025

@author: boogie
'''
from streams import StreamsBase, Test
from tinyxbmc import net
from tinyxbmc import mediaurl
from urllib import parse

import re
import unittest


class aliez(StreamsBase):
    regex = r"apl[0-9]+\.|aliez\.tv\/"

    def resolve(self, url, headers):
        page = net.http(url, headers=headers)
        up = parse.urlparse(url)
        hlsurl = re.search(r"init\((?:\'|\")(.+?)(?:\'|\")\)", page).group(1)
        origin = f"{up.scheme}://{up.netloc}"
        referer = origin + "/"
        hlsheaders = {"origin": origin,
                      "referer": referer}
        yield mediaurl.HlsUrl(net.absurl(hlsurl, url), hlsheaders, False)


class TestLink(unittest.TestCase, Test):
    link = "https://aliez.tv/live/1/"
