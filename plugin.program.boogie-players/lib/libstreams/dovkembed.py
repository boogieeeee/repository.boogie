'''
Created on Oct 7, 2025

@author: boogie
'''
from streams import StreamsBase
from tinyxbmc import net
from tinyxbmc import mediaurl

from urllib import parse

import re
import json


class dovk(StreamsBase):
    regex = r"dovkembed\.|viewembed\.ru"

    def resolve(self, url, headers):
        page = net.http(url, headers=headers)
        chan_key = re.search(r"channelKey\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")", page).group(1)
        apiurl = re.search(r"return\s*?fetchWithRetry\((?:\'|\")(.+?)(?:\'|\")", page).group(1) + chan_key
        hlsurl = re.search(r"m3u8\s*?=.+?:\s*?(?:\'|\"|`)(.+?)(?:\'|\"|`)", page, re.DOTALL).group(1)
        up = parse.urlparse(url)
        origin = f"{up.scheme}://{up.netloc}"
        referer = origin + "/"
        hlsheaders = {"origin": origin,
                      "referer": referer}
        serv_key = json.loads(net.http(apiurl, headers=hlsheaders))["server_key"]
        for k, v in {"${sk}": serv_key,
                     "${SK}": serv_key,
                     "${CHANNEL_KEY}": chan_key,
                     "${channel_key}": chan_key}.items():
            hlsurl = hlsurl.replace(k, v)
        yield mediaurl.HlsUrl(hlsurl, hlsheaders, True, False, lheaders=hlsheaders, aesparams="")
