from streams import StreamsBase
from tinyxbmc import net
import htmlement

from libstreams.third import packer

import re


class filemoon(StreamsBase):
    regex = r"filemoon\."

    def resolve(self, url, headers):
        xpage = htmlement.fromstring(net.http(url, headers=headers))
        iframe = net.http(xpage.find(".//iframe").get("src"))
        if packer.detect(iframe):
            iframe = packer.unpack(iframe)
        media = re.search(r"file\s*?:\s*?(?:\'|\")(.+?)(?:\'|\")", iframe)
        yield net.tokodiurl(net.absurl(media.group(1), url), headers=headers)
