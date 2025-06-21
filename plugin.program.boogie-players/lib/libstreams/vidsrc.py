'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
import htmlement
import re
import json

from six.moves.urllib import parse


class Vidsrc(StreamsBase):
    regex = r"vidsrc\.me"
    domain = "https://vidsrc.me"

    def resolve(self, url, headers):
        iframe = htmlement.fromstring(net.http(url, headers=headers)).find(".//iframe").get("src")
        url2 = self.domain + iframe
        page = net.http(url2, referer=url)
        vidpage = re.search(r'var\s*?query\s*?=\s*?(?:\'|")(.+?)(?:\'|")\;', page).group(1)
        resp = net.http(self.domain + "/watching" + vidpage, referer=url2, text=False)
        url3 = resp.url.replace("/v/", "/api/source/")
        headers = {"X-Requested-With": "XMLHttpRequest", "referer": resp.url}
        data = {"d": parse.urlparse(url3).netloc, "r": url2}
        js = json.loads(net.http(url3, headers=headers, data=data, method="POST"))
        if not js["success"]:
            print("VIDSRC ERROR: %s, %s" % (js["data"], url))
            yield
        for vid in js["data"]:
            yield net.tokodiurl(vid["file"], headers={"referer": resp.url})
