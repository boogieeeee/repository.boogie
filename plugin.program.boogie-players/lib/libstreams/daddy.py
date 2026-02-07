'''
Created on Oct 7, 2025

@author: boogie
'''
from streams import StreamsBase, Test
from libstreams import dovkembed
from tinyxbmc import net

import htmlement
import unittest


class dady(StreamsBase):
    regex = r"daddylive"

    def resolve(self, url, headers):
        xpage = htmlement.fromstring(net.http(url, headers=headers))
        iframe = xpage.find(".//iframe").get("src")
        d = dovkembed.dovk()
        headers["referer"] = url
        for media in d.resolve(iframe, headers):
            yield media


class TestLink(unittest.TestCase, Test):
    link = "https://daddylive4.click/live/stream-1.php"
