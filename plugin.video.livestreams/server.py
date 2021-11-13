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
        self.wait = 3
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

        # if iptvsimple auto configuration is requested execute it
        if base.config.pvr:
            base.iptvsimple.config_pvr()

    def onclose(self):
        # stop the server
        self.httpd.shutdown()
        logger.info("Livechannels m3u8 proxy stopped")

    def onloop(self):
        # runs each self.wait seconds
        if base.iptvsimple.isenabled() and not xbmc.Player().isPlaying():
            if not base.config.update_running and ((time.time() - base.config.lastupdate > common.check_timeout) or base.config.validate):
                Thread(target=base.do_validate, args=(True, self.isclosed())).start()
                # base.config.validate flag is reset in base.do_validate method
            if base.config.update_pvr:
                base.iptvsimple.reload_pvr()
                base.config.update_pvr = False
                time.sleep(1)
                base.iptvsimple.channels = base.iptvsimple.getchannels()
            if False and base.config.pvrrecord and base.config.pvrlocation:
                base.iptvsimple.shouldrecord()


Server()
