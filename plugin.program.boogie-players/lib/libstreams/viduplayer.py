'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
from third import packer
import re


class Vidsrc(StreamsBase):
    regex = "viduplayer\.com|supervideo\.tv|vidmoly\.to"

    def resolve(self, url, headers):
        page = net.http(url, headers=headers)
        if packer.detect(page):
            page = packer.unpack(page)
        for vid in re.findall("file\s*?\:\s*?(?:'|\")(.+?)(?:'|\")", page):
            if vid.endswith(".m3u8") or vid.endswith(".mp4") :
                headers = {"referer": url}
                yield net.tokodiurl(vid, headers=headers)
