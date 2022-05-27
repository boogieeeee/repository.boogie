'''
Created on Jul 16, 2021

@author: boogie
'''
# -*- encoding: utf-8 -*-
import ghub
import re
import os
from tinyxbmc import addon, tools, net
from liblivechannels import programme
from datetime import datetime
from io import open

UTC = tools.tz_utc()


ardundzdf = ghub.load("rols1", "Kodi-Addon-ARDundZDF", "master")
ghub.load("romanvm", "kodi.six", "master", path=["script.module.kodi-six", "libs"])

for target in ["util.py", "EPG.py"]:
    tfile = os.path.join(ardundzdf, "resources", "lib", target)
    with open(tfile, encoding="utf-8") as f:
        tcont = re.sub("plugin\.video\.ardundzdf", "plugin.video.livestreams", f.read())
        tcont = re.sub("xbmcaddon.Addon\(id=ADDON_ID\)", "xbmcaddon.Addon(ADDON_ID)", tcont)
        tcont = re.sub("ADDON_PATH[\s\t]*?=[\s\t]*?SETTINGS.getAddonInfo.+?\n", "ADDON_PATH = '%s'\n" % ardundzdf, tcont)
        tcont = re.sub("USERDATA[\s\t]*?=[\s\t]*?xbmcvfs.translatePath.+?\n", "USERDATA = '%s'\n" % os.path.abspath(os.path.join(addon.get_addondir("plugin.video.livestreams"), "")), tcont)
        tcont = re.sub("HANDLE[\s\t]*?=[\s\t]*?int.+?\n", "HANDLE = 1", tcont)
        tcont = re.sub("int\(SETTINGS\.getSetting\('pref_tv_store_days'\)\)", "1", tcont)
    with open(tfile, "w", encoding="utf-8") as f:
        f.write(tcont)


from resources.lib import util
from resources.lib import EPG

if not os.path.exists(util.ADDON_DATA):
    os.makedirs(util.ADDON_DATA)
util.check_DataStores()

e = EPG.EPG("ARD")


class multi():
    categories = ["Deutschland"]
    title = u"Das Erste"
    iconpath = os.path.join(ardundzdf, "resources", "images", "")
    usehlsproxy = False
    sender = "Das Erste"
    epg = None
    link = None

    def _link_epg(self):
        if not self.link or not self.epg:
            _, link, epg = util.get_playlist_img(self.sender)
        if not self.link:
            self.link = link
        if not self.epg:
            self.epg = epg

    def getlink(self):
        self._link_epg()
        return self.link

    def getepg(self):
        self._link_epg()
        return self.epg

    def get(self):
        link = self.getlink()
        if "ZDF" in self.sender:
            links = util.get_ZDFstreamlinks()
        elif "ARD" in link:
            links = util.get_ARDstreamlinks()
        elif "ZDF" in link:
            links = util.get_ZDFstreamlinks()
        else:
            yield net.hlsurl(link)
            raise StopIteration
        for link in links:
            sender, url, _img, _ = link.split("|")
            if sender == self.sender:
                yield net.hlsurl(url)
                break

    def iterprogrammes(self):
        epg = self.getepg()
        # delete cache first
        cachefile = os.path.join(util.DICTSTORE, "EPG_%s" % epg)
        if os.path.exists(cachefile):
            os.remove(cachefile)
        for start, _url, icon, prog1, _hour, desc, _fromto, _dt, end in EPG.EPG(epg):
            prog = re.sub("\[.*?\]", "", prog1).split("|")[-1].strip()
            start = datetime.utcfromtimestamp(int(start)).replace(tzinfo=UTC)
            end = datetime.utcfromtimestamp(int(end)).replace(tzinfo=UTC)
            yield programme(prog, start, end, icon=icon, desc=desc)
