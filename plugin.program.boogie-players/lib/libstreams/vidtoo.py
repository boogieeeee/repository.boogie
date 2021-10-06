'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
import re


class vidoo(StreamsBase):
    regex = "vidoo\.tv"

    def resolve(self, url, headers):
        for vid in re.finditer("file\s?\:\s?(?:\'|\")(.+?)(?:\'|\")", net.http(url, headers=headers)):
            yield net.tokodiurl(vid.group(1), headers={"referer": url})
