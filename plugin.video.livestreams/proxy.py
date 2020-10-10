from liblivechannels import log
from liblivechannels import proxy
from liblivechannels import common

from threading import Thread
from tinyxbmc import addon
from tinyxbmc import gui

from addon import Base

import time

import xbmc


PORT = 8000

base = Base(addon=common.addon_id)
proxy.Handler.base = base
logger = log.Logger(20)


class Server(addon.blockingloop):
    def init(self):
        self.wait = 1
        self.pvrenabled = False
        self.check_pvr()
        self.httpd = None
        base.config.update_running = False
        base.config.update_pvr = False
        if self.pvrenabled:
            while True:
                try:
                    port = base.config.port
                    self.httpd = proxy.ThreadedProxy(("", port), proxy.Handler)
                    break
                except Exception:
                    port += 1
                if not port == base.config.port:
                    base.config.port = port

    @property
    def isplaying(self):
        return xbmc.Player().isPlaying()

    def check_pvr(self):
        iptv = addon.addon_details("pvr.iptvsimple")
        if iptv:
            self.pvrenabled = iptv.get("enabled")

    def reload_pvr(self):
        self.check_pvr()
        if self.pvrenabled:
            time.sleep(1)
            addon.toggle_addon("pvr.iptvsimple")
            time.sleep(1)
            addon.toggle_addon("pvr.iptvsimple")

    def onloop(self):
        self.check_pvr()
        if self.pvrenabled and not self.isplaying:
            if not base.config.update_running and ((time.time() - base.config.lastupdate > common.check_timeout) or base.config.validate):
                Thread(target=self.update_thread).start()
            if base.config.update_pvr:
                self.reload_pvr()
                base.config.update_pvr = False
            if base.config.validate:
                base.config.validate = False

    def update_thread(self):
        base.do_validate(True, self.isclosed())

    def oninit(self):
        if self.pvrenabled:
            self.thread = Thread(target=self.httpd.serve_forever)
            self.thread.start()
            logger.info("Starting livestreams m3u8 proxy")
            if base.config.pvr:
                pvr_settings = addon.kodisetting("pvr.iptvsimple")
                if not pvr_settings.getint("m3uPathType") == 1:
                    pvr_settings.set("m3uPathType", 1)
                m3uurl = "http://localhost:%s" % base.config.port
                if not pvr_settings.getstr("m3uUrl") == m3uurl:
                    pvr_settings.set("m3uUrl", m3uurl)
                if not pvr_settings.getint("epgPathType") == 0:
                    pvr_settings.set("epgPathType", 0)
                if not pvr_settings.getstr("epgPath") == common.epath:
                    pvr_settings.set("epgPath", common.epath)
                self.reload_pvr()

    def onclose(self):
        if self.httpd:
            self.httpd.shutdown()
            logger.info("Livechannels m3u8 proxy stopped")


Server()
