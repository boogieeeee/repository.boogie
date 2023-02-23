# -*- encoding: utf-8 -*-
try:
    import unittest
    import test

    class TestSelcuk(unittest.TestCase):
        def test_selcuk_link(self):
            test.testlink(self, itermedias("bein1"), 1, "bein1", 0)

except ImportError:
    pass

from liblivechannels.chexts.scrapertools import normalize
from tinyxbmc import addon
from tinyxbmc import stubmod

selcukaddon = "service.vods.selcuk"


def itermedias(chfilter):
    if addon.has_addon(selcukaddon):
        addon.depend_addon(selcukaddon)
        import libselcuk
    else:
        raise StopIteration
    if chfilter:
        found = False
        for chid, _chlink, chname in libselcuk.iteratechannels():
            if chfilter == normalize(chname):
                found = True
                break
        if found:
            for media in libselcuk.getmedias(chid):
                yield media
