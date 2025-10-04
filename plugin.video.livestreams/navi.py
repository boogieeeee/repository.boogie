'''
Created on Feb 22, 2020

@author: boogie
'''
from addon import Base
from tinyxbmc import const


class Navi(Base):
    dropboxtoken = const.DB_TOKEN

    def index(self):
        channels = self.config.channels
        if self.config.validate or not len(channels):
            self.do_validate()

        for icon, title, index, cats, _url in channels:
            cats = [x.title() for x in cats]
            info = {"title": title}
            if icon:
                art = {"icon": icon, "thumb": icon, "poster": icon}
            else:
                art = {}
            item = self.item(title, info, art, method="geturls")
            cntx_select = self.item("Select Source", method="select_source")
            item.context(cntx_select, True, index)
            item.resolve(index)

    def select_source(self, cid):
        chan = self.loadchannel(cid)
        art = {"icon": chan.icon, "thumb": chan.icon, "poster": chan.icon}
        for url in chan.get():
            if not url:
                continue
            item = self.item("%s:%s" % (chan.title, url), art=art)
            item.resolve(url)

    def geturls(self, cid):
        chan = self.loadchannel(cid)
        for url in chan.get():
            if not url:
                continue
            yield url


Navi()
