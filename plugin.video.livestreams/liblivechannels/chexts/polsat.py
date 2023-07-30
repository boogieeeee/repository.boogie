# -*- encoding: utf-8 -*-
try:
    import unittest
    from test import ChannelTest

    class testpolsat(ChannelTest, unittest.TestCase):
        index = "polsat:polsatsport:"
        minepg = 1

    class testpolsatextra(ChannelTest, unittest.TestCase):
        index = "polsat:polsatsportextra:"
        minepg = 1

    class testpolsatnews(ChannelTest, unittest.TestCase):
        index = "polsat:polsatsportnews:"
        minepg = 1

    class testpolsatpremium1(ChannelTest, unittest.TestCase):
        index = "polsat:polsatpremium1:"
        minepg = 1

    class testpolsatnews(ChannelTest, unittest.TestCase):
        index = "polsat:polsatpremium2:"
        minepg = 1

except ImportError:
    pass


from liblivechannels.chexts.scrapertools.multi import multi
from liblivechannels import scraper
from liblivechannels import programme
from tinyxbmc import net
from tinyxbmc import tools
import json
from datetime import datetime

epgu = "https://www.polsatsport.pl/ajax-program-tv-column/module/"


class polsatsport(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Polsat_Sport_2021_gradient.svg/200px-Polsat_Sport_2021_gradient.svg.png"
    title = "Polsat Sport"
    categories = ["Polish", "Sport"]
    dady_name = "polsatsportpoland"
    acestreams = ["acestream://92b6ba09dae4bbb8a67a405125d08ca8d15380ee"]

    def iterprogrammes(self):
        for p in iterprogrammes("POLSAT Sport"):
            yield p


class polsatpremium1(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Polsat_Sport_Premium_1_2021_gradient.svg/320px-Polsat_Sport_Premium_1_2021_gradient.svg.png"
    title = "Polsat Sport Premium 1"
    categories = ["Polish", "Sport"]
    dady_name = "polsatsportpoland"
    acestreams = ["acestream://4ce55db7e578ff52a6e526cf610e477464b8a99f"]

    def iterprogrammes(self):
        for p in iterprogrammes("POLSAT Sport Premium 1"):
            yield p


class polsatpremium2(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Polsat_Sport_Premium_2_2021_gradient.svg/320px-Polsat_Sport_Premium_2_2021_gradient.svg.png"
    title = "Polsat Sport Premium 2"
    categories = ["Polish", "Sport"]
    dady_name = "polsatsportpoland"
    acestreams = ["acestream://3147c586346aee00c005d1caa55204d38678c95f"]

    def iterprogrammes(self):
        for p in iterprogrammes("POLSAT Sport Premium 2"):
            yield p


class polsatsportextra(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Polsat_Sport_Extra_2021_gradient.svg/240px-Polsat_Sport_Extra_2021_gradient.svg.png"
    title = "Polsat Sport Extra"
    categories = ["Polish", "Sport"]
    dady_name = "polsatsportextrapoland"
    acestreams = ["acestream://ef2cf11fc83f4f15a33c9a514a7afd2bce73122f"]
    
    def iterprogrammes(self):
        for p in iterprogrammes("POLSAT Sport Extra"):
            yield p



class polsatsportnews(multi, scraper):
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Polsat_Sport_News_2021_gradient.svg/240px-Polsat_Sport_News_2021_gradient.svg.png"
    title = "Polsat Sport News"
    categories = ["Polish", "Sport"]
    dady_name = "polsatsportnewspoland"

    def iterprogrammes(self):
        for p in iterprogrammes("POLSAT Sport News"):
            yield p


def iterprogrammes(polsatname):
    prevargs = {}
    for pagenum in [1, 2]:
        page = json.loads(net.http(epgu + "page%s" % pagenum, cache=None, encoding="utf-8"))
        for channel in page["channels"]:
            if channel["title"] == polsatname:
                for prog in channel["programs"]:
                    cur_start = datetime.fromtimestamp(prog["emissionDate"] / 1000)
                    cur_start.replace(tzinfo=tools.tz_utc())
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
