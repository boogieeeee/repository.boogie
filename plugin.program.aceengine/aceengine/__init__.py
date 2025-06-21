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
        self.id = None
        self.infohash = None
        if url.startswith("acestream://"):
            self.id = url.lower().replace("acestream://", "").strip()
        else:
            self.infohash = url
        self.stat_url = None
        self.command_url = None
        self.playback_url = None
        self.stats = {}
        self._token = None
        
    @property
    def token(self):
        if not self._token:
            params = {"method": "get_api_access_token"}
            jsdata = self.query("/server/api", params, ignore=True, key="result", cache=60)
            if jsdata:
                self._token = jsdata.get("token")
        return self._token
    
    def search(self, keyw, category="", page=0, pagesize=200, group_by_channels=1, show_epg=1, cache=None, ignore=True):
        params = {"method": "search",
                  "token": self.token,
                  "query": keyw,
                  "category": category,
                  "page": page,
                  "page_size": pagesize,
                  "group_by_channels": group_by_channels,
                  "show_epg": show_epg}
        print(self.token)
        return self.query("/server/api", params, key="result", cache=cache, ignore=ignore)

    def getstream(self, pid="kodi"):
        def _getstream():
            params = {"format": "json",
                      "pid": pid,
                      "id": self.id,
                      "infohash": self.infohash}
            jsdata = self.query("/ace/getstream", params, ignore=True)
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

    def query(self, uri, params, ignore=False, key="response", cache=None):
        try:
            if uri.startswith("/"):
                uri = self.apiurl() + uri
            jsdata = net.http(uri, params=params, cache=cache)
            jsdata = json.loads(jsdata)
        except Exception as e:
            jsdata = {"error": "Query Error %s" % e,
                      "response": None}
        if jsdata.get("error") and not ignore:
            raise AcestreamError(jsdata["error"])
        if key:
            return jsdata.get(key)
        else:
            return jsdata
        
        
    def updatestats(self):
        stats = self.query(self.stat_url, None, ignore=True)
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
            params = {"method": "stop"}
            retval = self.query(url, params, ignore=True) == "ok"
            return retval is None or retval
    
    @staticmethod
    def apiurl():
        return settings.getstr(const.SETTING_ACTIVEADDRESS)
