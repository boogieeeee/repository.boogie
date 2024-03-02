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
        self.lastupdate = 0

    def getstream(self, force=False):
        if not self.playback_url or force:
            jsdata = self.query("%s/ace/getstream?id=%s&format=json" % (acestream.apiurl(), self.id), ignore=False)
            if jsdata:
                self.stat_url = jsdata["stat_url"]
                self.command_url = jsdata["command_url"]
                self.playback_url = jsdata["playback_url"]
                self.updatestats()
    
    @property
    def httpurl(self):
        self.stopall()
        self.getstream()
        return self.playback_url

    def stopall(self, ignoreme=True):
        with hay.stack(const.STREAMHAY, aid=const.ADDONID) as streamhay:
            streams = streamhay.find(const.STREAMHAY_KEY).data
            for sid in list(streams.keys()):
                if ignoreme and sid == self.id:
                    continue
                self.stop(streams[sid][2])
                streams.pop(sid)
            streams[self.id] = (self.stat_url, self.command_url, self.playback_url)
            streamhay.throw(const.STREAMHAY_KEY, streams)

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
        if (time.time() - self.lastupdate) > 1:
            stats = self.query(self.stat_url, ignore=True)
            if stats:
                self.stats = stats
                self.lastupdate = time.time()
        
    @property
    def hasstarted(self):
        self.updatestats()
        return self.stats.get("status") == "dl"
        
    def stop(self, url=None):
        if not url:
            url = self.command_url
        if url:
            retval = self.query(url + "?method=stop", ignore=True) == "ok"
            return retval is None or retval == "ok"
    
    @staticmethod
    def apiurl():
        return settings.getstr(const.SETTING_ACTIVEADDRESS)
