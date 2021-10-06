import unittest
import sys
import os
sys.argv[0] = "plugin://plugin.video.livestreams"

from tinyxbmc import net
from tinyxbmc import stubmod
from tinyxbmc import tools

stubmod.rootpath = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import addon


base = addon.Base()


class ChannelTest():
    minlinks = 1
    minepg = 1
    thumbnail = True

    def setUp(self):
        for channel in base.iterchannels():
            if channel.index == self.index:
                self.channel = channel(net.http)
                break

    def test_links(self):
        valids = []
        invalids = []
        error = None
        if self.channel.checkerrors is not None:
            error = self.channel.checkerrors()
        if error is None:
            for link in tools.safeiter(self.channel.get()):
                error = base.healthcheck(link)
                if error is not None:
                    invalids.append((error, link))
                else:
                    valids.append(link)
        self.assertFalse(self.minlinks > len(valids), "%s, %s, Minimum requried link is %s but available is %s."
                                                      "Invalids:%s"
                                                      "Valids:%s" % (self.channel.title,
                                                                     self.channel.index,
                                                                     self.minlinks,
                                                                     len(valids),
                                                                     invalids,
                                                                     valids))

    def test_thumbnail(self):
        if self.thumbnail:
            self.assertFalse(self.channel.icon is None)
            self.assertFalse(self.channel.icon == "DefaultFolder.png")
            if self.channel.icon.startswith("http"):
                self.assertFalse(net.http(self.channel.icon, method="HEAD") is None)

    def test_epg(self):
        if self.minepg:
            self.assertTrue(len(list(self.channel.iterprogrammes())) >= self.minepg)
