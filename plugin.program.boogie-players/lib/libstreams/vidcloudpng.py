'''
Created on Nov 21, 2019

@author: boogie
'''
"""
from streams import StreamsBase
from tinyxbmc import net
import time
import urlparse


class vidcloudpng(StreamsBase):
    regex = "vidcloudpng\.com"

    def resolve(self, url, headers):
        up = urlparse.urlparse(url)
        vurl = "https://%s/playlist/%s/%s" % (up.netloc,
                                              dict(urlparse.parse_qsl(up.query))["id"],
                                              int(time.time() * 1000))
        yield net.tokodiurl(vurl, headers={"referer": url})
"""
