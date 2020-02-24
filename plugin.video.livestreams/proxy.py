from liblivechannels import log
from liblivechannels import proxy
from liblivechannels import common

from threading import Thread
from tinyxbmc import addon

from addon import Base

import time

logger = log.Logger()

PORT = 8000

base = Base(addon=common.addon_id)
proxy.Handler.base = base


class Server(addon.blockingloop):
    def init(self):
        self.pvrenabled = False
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
                time.sleep(1)
                addon.toggle_addon("pvr.iptvsimple")
                time.sleep(1)
                addon.toggle_addon("pvr.iptvsimple")

    def onclose(self):
        if self.pvrenabled:
            self.httpd.shutdown()
            logger.info("Livechannels m3u8 proxy stopped")


Server()
