'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
import re


class Vidsrc(StreamsBase):
    regex = "vidnode\.net"
    domain = "https://vidnode.net"

    def resolve(self, url, headers):
        page = net.http(url, headers=headers)
        m3us = re.findall("urlVideo\s*?\=\s*?(?:'|\")(.+?)(?:'|\")", page)
        for m3u in m3us:
            if not m3u.endswith("playlist.m3u8"):
                continue
            headers = {"referer": url}
            yield net.tokodiurl(m3u, headers=headers)
