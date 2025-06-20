from streams import StreamsBase
from tinyxbmc import net

import re


class sibnet(StreamsBase):
    regex = r"sibnet\.ru"

    def resolve(self, url, headers):
        page = net.http(url, headers=headers)
        media = re.search(r"src\s*?:\s*?(?:\'|\")(.+?)(?:\'|\")", page)
        yield net.tokodiurl(net.absurl(media.group(1), url), headers={"Referer": url})
