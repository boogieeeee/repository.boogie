'''
Created on Feb 22, 2020

@author: boogie
'''
from addon import Base
import liblivechannels
from tinyxbmc import tools


class Navi(Base):
    def cats(self):
        for cat in tools.safeiter(liblivechannels.getcategories()):
            self.item(cat, method="index").dir(cat)

    def index(self, cat=None):
        if not cat:
            self.item("Categories", method="cats").dir()
        for icon, title, index, cats in self.channels.get("alives", []):
            if cat and cat not in cats:
                continue
            info = {"title": title}
            art = {"icon": icon, "thumb": icon, "poster": icon}
            self.item(title, info, art, method="geturls").resolve(index)

    def geturls(self, cid):
        chan = liblivechannels.loadchannel(cid, self.download)
        for url in chan.get():
            yield url


Navi()
