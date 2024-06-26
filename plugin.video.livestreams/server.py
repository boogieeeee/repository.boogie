from liblivechannels import log
from liblivechannels import proxy
from liblivechannels import common

from threading import Thread
from tinyxbmc import addon
from tinyxbmc import const

from addon import Base

import time
import xbmc

PORT = 8000

base = Base(addonid=common.addon_id)
proxy.Handler.base = base
logger = log.Logger(20)


class Server(addon.blockingloop):
    def init(self):
        self.wait = 5
        self.dropboxtoken = const.DB_TOKEN

    def oninit(self):
        base.config.update_running = False
        # start server on a free port
        while True:
            try:
                port = base.config.port
                self.httpd = proxy.ThreadedProxy(("", port), proxy.Handler)
                break
            except Exception:
                port += 1
            # if port is different than configged update the port in config
            if not port == base.config.port:
                base.config.port = port

        logger.info("Starting livestreams m3u8 proxy")
        self.thread = Thread(target=self.httpd.serve_forever)
        self.thread.start()
        self.pvrtimer = base.config.pvrtimer

    def onclose(self):
        # stop the server
        self.httpd.shutdown()
        logger.info("Livechannels m3u8 proxy stopped")
        
    def validatechannels(self):
        if not base.config.update_running:
            deltat = time.time() - base.config.updatetime
            if (deltat >= 0 and deltat <= 60 * 60 and base.config.lastupdate < base.config.updatetime) or base.config.validate:
                if base.config.validate:
                    base.config.validate = False
                base.config.lastupdate = time.time()
                Thread(target=base.do_validate, args=(True, self.isclosed)).start()
                
    def reloadpvr(self):
        if self.pvrtimer:
            self.pvrtimer -= self.wait
            self.pvrtimer = -1 if not self.pvrtimer else self.pvrtimer
        if base.config.update_pvr or self.pvrtimer < 0:
            self.pvrtimer = 0
            base.iptvsimple.reload_pvr()
            base.config.update_pvr = False
            base.iptvsimple.channels = base.iptvsimple.getchannels()
            
    def configpvr(self):
        if base.config.pvr:
            base.iptvsimple.config_pvr()
            base.config.pvr = False
            base.iptvsimple.reload_pvr()

    def onloop(self):
        # runs each self.wait seconds
        if base.iptvsimple.isenabled() and not xbmc.Player().isPlaying():
            self.validatechannels()
            self.reloadpvr()
            self.configpvr()

Server()
