# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testpolsat(ChannelTest, unittest.TestCase):
        index = "polsat:polsatsport:"
        minepg = 1

except ImportError:
    pass


from liblivechannels.chexts.scrapertools.multi import multi
from liblivechannels import scraper
from liblivechannels import programme
from tinyxbmc import net
import json
from datetime import datetime

epgu = "https://www.polsatsport.pl/ajax-program-tv-column/module/"


class polsatsport(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Polsat_Sport_2021_gradient.svg/200px-Polsat_Sport_2021_gradient.svg.png"
    title = "Polsat Sport"
    categories = ["Polish", "Sport"]
    dady_name = "polsatsportpoland"
    usehlsproxy = True

    def iterprogrammes(self):
        for p in iterprogrammes("POLSAT Sport"):
            yield p


class polsatsportextra(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Polsat_Sport_Extra_2021_gradient.svg/240px-Polsat_Sport_Extra_2021_gradient.svg.png"
    title = "Polsat Sport Extra"
    categories = ["Polish", "Sport"]
    dady_name = "polsatsportextrapoland"
    usehlsproxy = True

    def iterprogrammes(self):
        for p in iterprogrammes("POLSAT Sport Extra"):
            yield p


class polsatsportnews(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Polsat_Sport_News_2021_gradient.svg/240px-Polsat_Sport_News_2021_gradient.svg.png"
    title = "Polsat Sport News"
    categories = ["Polish", "Sport"]
    dady_name = "polsatsportnewspoland"
    usehlsproxy = True

    def iterprogrammes(self):
        for p in iterprogrammes("POLSAT Sport News"):
            yield p


def iterprogrammes(polsatname):
    prevargs = {}
    for pagenum in [1, 2]:
        page = json.loads(net.http(epgu + "page%s" % pagenum, cache=None))
        for channel in page["channels"]:
            if channel["title"] == polsatname:
                for prog in channel["programs"]:
                    cur_start = datetime.fromtimestamp(prog["emissionDate"] / 1000)
                    if prevargs:
                        kwargs = {"end": cur_start}
                        kwargs.update(prevargs)
                        yield programme(**kwargs)
                    desc = None
                    for k in "description", "preview", "progDescription":
                        desc = prog.get(k)
                        if desc:
                            break
                    prevargs = {"title": prog["title"],
                                "start": cur_start,
                                "icon": prog.get("miniImageUrl"),
                                "desc": desc}
