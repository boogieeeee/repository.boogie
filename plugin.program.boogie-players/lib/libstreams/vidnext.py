'''
Created on Nov 21, 2019

@author: boogie
'''
from streams import StreamsBase
import htmlement
import urlparse
import json
from operator import itemgetter
from tinyxbmc import net


class Vidnext(StreamsBase):
    regex = "movcloud\.net|vidnext\.net"

    def resolve(self, url, headers):
        if "vidnext" in url:
            page = net.http(url, headers=headers)
            tree = htmlement.fromstring(page)
            iframe = tree.find(".//iframe[@id='embedvideo_main']")
            if iframe is not None:
                headers["referer"] = url
                url = iframe.get("src")
            else:
                up = urlparse.urlparse(url)
                jsq = dict(urlparse.parse_qsl(up.query))
                jsurl = "https://%s/ajax.php" % up.netloc
                js = json.loads(net.http(jsurl, params=jsq, referer=url, headers={"x-requested-with": "XMLHttpRequest"}))
                for k in ["source", "source_bk"]:
                    for vid in js.get(k, []):
                        yield net.tokodiurl(vid["file"], headers={"referer": url})
        up = urlparse.urlparse(url)
        if "movcloud.net" in url:
            vid = up.path.split("/")[-1]
            jsurl = "https://api.%s/stream/%s" % (up.netloc, vid)
            print jsurl
            js = json.loads(net.http(jsurl, referer=url))
            print js
            for vid in sorted(js["data"]["sources"], key=itemgetter("height"), reverse=True):
                yield net.tokodiurl(vid["file"], headers={"referer": url})
        else:
            raise Exception("unknown url:%s" % url)
