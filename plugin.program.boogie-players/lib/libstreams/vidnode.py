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
        for m3u in re.findall("file\s*?\:\s*?(?:'|\")(.+?)(?:'|\")", page):
            if not re.search("sub\.[0-9]+?.\m3u8", m3u):
                continue
            headers = {"referer": url}
            yield net.tokodiurl(m3u, headers=headers)
