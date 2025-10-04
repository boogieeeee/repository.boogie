from streams import StreamsBase
from tinyxbmc import net
from tinyxbmc import mediaurl
from libstreams.third import packer

import re


class spcdn(StreamsBase):
    regex = r"rubyvidhub\.com"

    def resolve(self, url, headers):
        page = net.http(url, headers=headers)
        if packer.detect(page):
            page = packer.unpack(page)
        media = re.search(r"sources.+?file:(?:\"|\')(.+?)(?:\"|\')", page)
        yield mediaurl.LinkUrl(media.group(1))
