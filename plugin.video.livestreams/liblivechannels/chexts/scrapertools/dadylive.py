try:
    import unittest
    import test

    class testdaddy(unittest.TestCase):
        def test_daddy_link(self):
            test.testlink(self, itermedias(None, "beinsports1turkey"), 1, "Bein1", 0)

except ImportError:
    pass

from tinyxbmc import addon
from tinyxbmc import stubmod

daddyaddon = "service.vods.poscitech"


def itermedias(dadyid=None, dadyname=None):
    if addon.has_addon(daddyaddon):
        addon.depend_addon(daddyaddon)
        import liblivetvon
    else:
        raise StopIteration
    if not dadyid:
        dadyid = liblivetvon.getchmeta(nameidbynum=True)[dadyname]
    yield liblivetvon.geturl(dadyid)
