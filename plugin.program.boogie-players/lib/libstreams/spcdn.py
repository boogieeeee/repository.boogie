from streams import StreamsBase
from tinyxbmc import net
import re
from urllib.parse import urlparse

class spcdn(StreamsBase):
    regex = "spcdn\.(?:.+?\/player)"

    def resolve(self, url, headers):
        page = net.http(url, headers=headers)
        link = re.search("(?:\"|\')videoUrl(?:\"|\')\s*?\:\s*?(?:\"|\')(.+?)(?:\"|\')", page)
        if link:
            up = urlparse(url)
            domain = "%s://%s" % (up.scheme, up.netloc)
            link = link.group(1).replace("\\", "")
            yield net.tokodiurl(domain + link + "?s=1&d=", headers={"referer": url})