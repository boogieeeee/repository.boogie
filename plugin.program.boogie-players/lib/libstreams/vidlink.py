'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
import re
import json
from six.moves.urllib.parse import urlparse


class Vidlink(StreamsBase):
    regex = "vidlink\.org|ronemo\.com"

    def resolve(self, url, headers):
        if "vidlink.org" in url:
            postid = re.search("postID\s?\=\s?(?:\'|\")(.+?)(?:\'|\")", net.http(url, headers=headers))
            up = urlparse(url)
            jsurl = "https://%s/embed/info?postID=%s" % (up.netloc, postid.group(1))
            js = json.loads(net.http(jsurl, referer=url))
            url = js["embed_urls"]
        if "ronemo.com" in url:
            up = urlparse(url)
            jsurl = "https://%s/api/video/get-link?idVid=%s" % (up.netloc, up.path.split("/")[-1])
            js = json.loads(net.http(jsurl, referer=url))
            yield net.tokodiurl("https://hls.ronemo.com/%s" % js["link"], headers={"referer": url})
