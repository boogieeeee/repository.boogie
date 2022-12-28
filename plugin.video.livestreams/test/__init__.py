import unittest
import sys
import os
sys.argv[0] = "plugin://plugin.video.livestreams"

from tinyxbmc import net
from tinyxbmc import stubmod
from tinyxbmc import tools
import addon

# stubmod.rootpath = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

base = addon.Base()


def testlink(unit, it, minlinks, title, index):
    valids = []
    invalids = []
    for link in tools.safeiter(it):
        error, _resp, _headers = base.healthcheck(link)
        if error is not None:
            invalids.append((error, link))
        else:
            valids.append(link)
    unit.assertFalse(minlinks > len(valids), "%s, %s, Minimum requried link is %s but available is %s."
                                             "Invalids:%s"
                                             "Valids:%s" % (title,
                                                            index,
                                                            minlinks,
                                                            len(valids),
                                                            invalids,
                                                            valids))


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
        error = None
        if self.channel.checkerrors is not None:
            error = self.channel.checkerrors()
        if error is None:
            testlink(self, self.channel.get(), self.minlinks, self.channel.title, self.channel.index)

    def test_thumbnail(self):
        if self.thumbnail:
            self.assertFalse(self.channel.icon is None)
            self.assertFalse(self.channel.icon == "DefaultFolder.png")
            if self.channel.icon.startswith("http"):
                self.assertFalse(net.http(self.channel.icon, method="HEAD") is None)

    def test_epg(self):
        if self.minepg:
            self.assertTrue(len(list(self.channel.iterprogrammes())) >= self.minepg)
