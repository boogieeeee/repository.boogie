'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
from tinyxbmc import mediaurl
import re


class vidoo(StreamsBase):
    regex = r"vidoo\.tv"

    def resolve(self, url, headers):
        for vid in re.finditer(r"file\s?\:\s?(?:\'|\")(.+?)(?:\'|\")", net.http(url, headers=headers)):
            yield mediaurl.LinkUrl(vid.group(1), headers={"referer": url})
