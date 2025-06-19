# -*- coding: utf-8 -*-

import re
import vods
from tinyxbmc import const
from tinyxbmc import net
from tinyxbmc import mediaurl
import aceengine


cats = ["informational",
        "entertaining",
        "educational",
        "movies",
        "documentaries",
        "sport",
        "fashion",
        "music",
        "regional",
        "ethnic",
        "religion",
        "teleshop",
        "erotic_18_plus",
        "other_18_plus",
        "cyber_games",
        "amateur",
        "webcam"]


class ace(vods.movieextension):
    useaddonplayers = False
    uselinkplayers = False
    loadtimeout = 3
    dropboxtoken = const.DB_TOKEN
    
    def searchmovies(self, keyw):
        self.getmovies(cat="", keyw=keyw)

    def getcategories(self):
        for cat in cats:
            catname = cat.replace("_", " ").title()
            self.additem(catname, cat)

    def getmovies(self, cat="", keyw=""):
        engine = aceengine.acestream("")
        page = 0
        total = None
        while True:
            response = engine.search(keyw, cat, page=page)
            if total is None:
                total = response.get("total", 0)
            results = response.get("results", [])
            total -= len(results)
            page += 1
            for result in results:
                name = str(result["name"])
                items = result["items"]
                art = None
                img = result.get("icons")
                if img:
                    art = {"icon": img[0]["url"],
                           "thumb": img[0]["url"],
                           "poster": img[0]["url"],
                           }
                epg = result.get("epg")
                if epg:
                    name += f" [{epg[0]['name']}]"
                self.additem(name, items, art=art)
            if total <= 0:
                break

    def geturls(self, items):
        for item in items:
            yield mediaurl.acestreamurl(item["infohash"])
