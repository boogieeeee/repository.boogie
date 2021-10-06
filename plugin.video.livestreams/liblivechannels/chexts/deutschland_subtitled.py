# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testbr(ChannelTest, unittest.TestCase):
        index = "deutschland_subtitled:br:"
        minepg = 0

    class testdaserste(ChannelTest, unittest.TestCase):
        index = "deutschland_subtitled:daserste:"
        minepg = 0

except ImportError:
    pass


from tinyxbmc import net
from liblivechannels import scraper
import re
import json


class br(scraper):
    domain = "https://www.br.de"
    categories = ["Deutschland", "Subtitled"]
    title = u"BR [ÜT]"
    icon = domain + "/unternehmen/inhalt/rundfunkrat/br-fernsehen-logo-neu-102~_v-img__16__9__xl_-d31c35f8186ebeb80b0cd843a7c267a0e0c81647.jpg?version=2b06d"
    usehlsproxy = False

    def get(self):
        page = self.download(self.domain + "/mediathek/live")
        link = re.search(r'publicLocation.+?"(.+?)"', page)
        yield net.hlsurl(link.group(1))


class daserste(scraper):
    domain = "https://live.daserste.de/"
    categories = ["Deutschland", "Subtitled"]
    title = u"Das Erste [ÜT]"
    icon = domain + "/mediasrc/img/tv/ard/ard-daserste-logo.png"
    usehlsproxy = False

    def get(self):
        page = self.download(self.domain)
        js = re.search(r'data-ctrl-player="(.+?)"', page).group(1)
        js = re.search(r'url(?:\'|\")\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")', js).group(1)
        jsdata = json.loads(self.download(self.domain + js, referer=self.domain))
        yield net.hlsurl(jsdata["mc"]["_alternativeMediaArray"][0]["_mediaArray"][0]["_mediaStreamArray"][0]["_stream"][0])
