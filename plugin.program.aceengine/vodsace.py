# -*- coding: utf-8 -*-

import vods
from tinyxbmc import const
from tinyxbmc import mediaurl
from tinyxbmc import iso
import aceengine


adult_filter = True
adult_kw = ["18+", "+18", "18 plus", "plus 18", "adult", "porn", "sex", "erotic"]


class ace(vods.movieextension):
    useaddonplayers = False
    uselinkplayers = False
    loadtimeout = 3
    dropboxtoken = const.DB_TOKEN
    
    def searchmovies(self, keyw):
        self.getmovies(cat="", keyw=keyw)
        
    def getcats(self, result):
        cats = []
        
        def _add_cat(name):
            name = name.replace("_", " ").title().strip()
            if name and name not in cats:
                cats.append(name)
        
        for item in result.get("items", []):
            for cat in item.get("categories", []):
                _add_cat(cat)
            for lang in item.get("languages", []):
                lang = iso.languages_3letter.get(lang.lower(), lang)
                _add_cat(lang)
            for country in item.get("countries", []):
                country = iso.countries_2letter.get(country.lower(), country)
                _add_cat(country)
            if item.get("disabled"):
                _add_cat("disabled")
            status = item.get("status")
            if status == 1:
                _add_=_add_cat("health status yellow")
            if status == 2:
                _add_cat("health status green")
            epg = result.get("epg")
            if epg:
                _add_cat("with epg")
        return cats

    def getcategories(self):
        cats = {}
        for result in self.iterresults():
            for subcat in self.getcats(result):
                if subcat not in cats:
                    cats[subcat] = 1
                else:
                    cats[subcat] += 1
        
        for cat, count in sorted(cats.items()):
            if adult_filter and self.isadult(cat, []):
                continue
            self.additem(f"{cat} ({count})", cat)
    
    def iterresults(self, cat="", keyw=""):
        engine = aceengine.acestream("")
        page = 0
        total = None
        while True:
            response = engine.search(keyw, cat, page=page, cache=60, ignore=False)
            if not response:
                return
            if total is None:
                total = response.get("total", 0)
            results = response.get("results", [])
            total -= len(results)
            page += 1
            for result in results:
                yield result
            if total <= 0:
                break
    
    def isadult(self, name, cats):
        name = name.lower()
        for kw in adult_kw:
            if kw in name:
                return True
        for cat in cats:
            cat = cat.lower()
            for kw in adult_kw:
                if kw in cat:
                    return True
        return False

    def getmovies(self, cat="", keyw=""):
        channels = []
        for result in self.iterresults("", keyw):
            cats = self.getcats(result)
            if cat and cat not in cats:
                continue
            name = str(result["name"])
            if adult_filter and self.isadult(name, cats):
                continue
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
            channels.append([name, items, None, art])
        
        channels.sort()
        
        for channel in channels:
            self.additem(*channel)


    def geturls(self, items):
        for item in items:
            yield mediaurl.acestreamurl(item["infohash"])
