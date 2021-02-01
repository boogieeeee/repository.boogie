# -*- encoding: utf-8 -*-
import re

from liblivechannels import scraper
from tinyxbmc import net


domain = "https://www.dmax.com.tr"

class dmax(scraper):
    title = u"DMAX"
    categories = [u"Türkçe", u"Realiti"]
    icon = domain + "/assets/theme/assets/images/white_logo.png"
    usehlsproxy = False

    def get(self):
        u = domain + "/canli-izle"
        pg = self.download(u, referer=domain)
        rgx = 'liveUrl\s*?=\s*?"(.+?)"'
        jsu = re.search(rgx, pg).group(1)
        js = self.download(jsu.replace("/dmax?", "/dmaxdai?") + "&json=true", referer=u, json=True)
        yield net.tokodiurl(js["xtra"]["url"], headers={"Referer": u})
        
