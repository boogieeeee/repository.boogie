from liblivechannels import log
logger = log.Logger(10)
from liblivechannels import proxy
from liblivechannels import common

from threading import Thread
from tinyxbmc import addon

from addon import Base

import time

import xbmc


PORT = 8000

base = Base(addon=common.addon_id)
proxy.Handler.base = base


class Server(addon.blockingloop):
    def init(self):
        self.wait = 1
        self.pvrenabled = False
        self.updaterunning = False
        self.deffered_pvr_update = False
        iptv = addon.addon_details("pvr.iptvsimple")
        if iptv:
            self.pvrenabled = iptv.get("enabled")
        if self.pvrenabled:
            while True:
                try:
                    port = base.port
                    self.httpd = proxy.ThreadedProxy(("", port), proxy.Handler)
                    break
                except Exception:
                    port += 1
                if not port == base.port:
                    base.port = port
                    
    def onloop(self):
        if not self.updaterunning and time.time() - base.lastupdate > common.check_timeout:
            Thread(target=self.update_thread).start()
        if not xbmc.Player().isPlaying() and self.deffered_pvr_update:
            self.reload_pvr()
            self.deffered_pvr_update = False
            
    def update_thread(self):
        self.updaterunning = True
        base.do_validate(base.hay("chan"), True, self.isclosed())
        self.deffered_pvr_update = True
        self.updaterunning = False

    def oninit(self):
        if self.pvrenabled:
            self.thread = Thread(target=self.httpd.serve_forever)
            self.thread.start()
            logger.info("Starting livechannels m3u8 proxy")
            if base.pvr:
                pvr_settings = addon.kodisetting("pvr.iptvsimple")
                if not pvr_settings.getint("m3uPathType") == 1:
                    pvr_settings.set("m3uPathType", 1)
                m3uurl = "http://localhost:%s" % base.port
                if not pvr_settings.getstr("m3uUrl") == m3uurl:
                    pvr_settings.set("m3uUrl", m3uurl)
                self.reload_pvr()
                
    def reload_pvr(self):
        time.sleep(1)
        addon.toggle_addon("pvr.iptvsimple")
        time.sleep(1)
        addon.toggle_addon("pvr.iptvsimple")


    def onclose(self):
        if self.pvrenabled:
            self.httpd.shutdown()
            logger.info("Livechannels m3u8 proxy stopped")


Server()
