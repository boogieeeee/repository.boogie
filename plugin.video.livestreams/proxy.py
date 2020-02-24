from liblivechannels import log
from liblivechannels import proxy
from threading import Thread
from tinyxbmc import addon

logger = log.Logger()

PORT = 8000


class Server(addon.blockingloop):
    def init(self):
        self.httpd = proxy.ThreadedProxy(("", PORT), proxy.Handler)

    def oninit(self):
        self.thread = Thread(target=self.httpd.serve_forever)
        self.thread.start()
        logger.info("Starting livechannels m3u8 proxy")

    def onclose(self):
        self.httpd.shutdown()
        logger.info("Livechannels m3u8 proxy stopped")


Server()
