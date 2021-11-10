'''
Created on Nov 21, 2019

@author: boogie
'''
from vods import linkplayerextension
from tinyxbmc import extension
from tinyxbmc import tools
from tinyxbmc import const
import re
import os

ppath = os.path.join(os.path.dirname(__file__), "libstreams")


class StreamsBase(object):
    regex = None

    def resolve(self, url, headers):
        return url


class streams(linkplayerextension):
    title = "Streams Link Extension"
    dropboxtoken = const.DB_TOKEN

    def init(self):
        self.providers = [x[1] for x in extension.getobjects(ppath, parents=[StreamsBase])]

    def geturls(self, url, headers=None):
        for provider in self.providers:
            if provider.regex and re.search(provider.regex, url):
                for url in tools.safeiter(provider().resolve(url, headers)):
                    yield url
                break
