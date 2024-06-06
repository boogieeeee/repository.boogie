import time
import json

from . import const
from tinyxbmc import addon
from tinyxbmc import net
from tinyxbmc import hay
import aceengine


settings = addon.kodisetting(const.ADDONID)

class AcestreamError(Exception):
    pass


class acestream():
    def __init__(self, url):
        self.url = url
        self.id = url.lower().replace("acestream://", "").strip()
        self.stat_url = None
        self.command_url = None
        self.playback_url = None
        self.stats = {}

    def getstream(self, pid="kodi"):
        def _getstream():
            jsdata = self.query("%s/ace/getstream?id=%s&format=json&pid=%s" % (acestream.apiurl(), self.id, pid), ignore=False)
            if jsdata:
                self.stat_url = jsdata["stat_url"]
                self.command_url = jsdata["command_url"]
                self.playback_url = jsdata["playback_url"]
                self.updatestats()
        _getstream()
        if self.hasstarted:
            self.stop()
            _getstream()

    @property
    def httpurl(self):
        self.getstream()
        return self.playback_url

    def query(self, uri, ignore=False):
        try:
            jsdata = net.http(uri, cache=None)
            jsdata = json.loads(jsdata)
        except Exception as e:
            jsdata = {"error": "Query Error %s" % e,
                      "response": None}
        if jsdata.get("error") and not ignore:
            raise AcestreamError(jsdata["error"])
        return jsdata.get("response")
        
    def updatestats(self):
        stats = self.query(self.stat_url, ignore=True)
        if stats:
            self.stats = stats
        
    @property
    def hasstarted(self):
        self.updatestats()
        return self.stats.get("status") == "dl"
        
    def stop(self, url=None):
        if not url:
            url = self.command_url
        if url:
            retval = self.query(url + "?method=stop", ignore=True) == "ok"
            return retval is None or retval
    
    @staticmethod
    def apiurl():
        return settings.getstr(const.SETTING_ACTIVEADDRESS)
