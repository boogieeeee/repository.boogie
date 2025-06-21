'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
import json


class vidcloud9(StreamsBase):
    regex = r"vidcloud9\.com|vidnode\.net"
    domain = "https://vidcloud9.com"

    def resolve(self, url, headers):
        if url.endswith(".m3u8"):
            yield net.tokodiurl(url, headers=headers)
        else:
            url = url.replace("/streaming.php", "/ajax.php")
            url = url.replace("/load.php", "/ajax.php")
            headers = {"x-requested-with": "XMLHttpRequest"}
            jpage = net.http(url, headers=headers, referer=self.domain)
            js = json.loads(jpage)
            for src in js["source"]:
                yield net.tokodiurl(src["file"], headers={"referer": self.domain})
