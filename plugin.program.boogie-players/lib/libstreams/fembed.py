'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
import json
import urlparse


def sorter(obj):
    return int(obj["label"].replace("p", ""))


class Fembed(StreamsBase):
    regex = "fembed\.net|fembed\.com|feurl\.com"

    def resolve(self, url, headers):
        resp = net.http(url, headers=headers, text=False, stream=True)
        up = urlparse.urlparse(resp.url)
        api_url = up.scheme + "://" + up.netloc + "/api/source/" + up.path.split("/")[-1]
        data = {"r": "", "d": up.netloc}
        jsdata = net.http(api_url, referer=resp.url, data=data, method="POST")
        for data in sorted(json.loads(jsdata)["data"], key=sorter, reverse=True):
            yield data["file"]
