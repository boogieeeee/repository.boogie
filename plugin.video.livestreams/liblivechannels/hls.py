import threading
import Queue
import time
import urlparse
import urllib
import json

from liblivechannels import common
from thirdparty.m3u8 import model

from tinyxbmc import addon


class PlaylistGenerator(object):
    def __init__(self, base):
        self.base = base
        self.playlists = Queue.Queue()
        self.__threads = []
        self.index = 10

    @staticmethod
    def sorter(playlist):
        return playlist.stream_info.bandwidth

    def add(self, m3file, headers):
        if len(m3file.playlists):
            for playlist in sorted(m3file.playlists, key=self.sorter, reverse=True):
                if self.base.resolve_mode == 0:
                    self.headcheck(playlist, headers)
                    if self.playlists.qsize():
                        break
                else:
                    thread = threading.Thread(target=self.headcheck, args=(playlist, headers))
                    thread.start()
                    self.__threads.append(thread)
        elif len(m3file.segments):
            self.index += 1
            playlist = model.Playlist(m3file.full_uri,
                                      {"bandwidth": self.index},
                                      None, m3file.base_uri)
            self.playlists.put((playlist, headers))

    def headcheck(self, playlist, headers):
        networkerr = False
        try:
            resp = self.base.download(playlist.absolute_uri, headers=headers, method="HEAD",
                                      timeout=common.query_timeout)
        except Exception:
            networkerr = True
        if not networkerr and resp.status_code == 200:
            self.playlists.put((playlist, headers))
        else:
            try:
                resp = self.base.download(playlist.absolute_uri, headers=headers,
                                          text=False, timeout=common.query_timeout)
            except Exception:
                return
            if resp.content[:7] == "#EXTM3U":
                self.playlists.put((playlist, headers))
        pass
    
    def wait(self):
        starttime = time.time()
        for thread in self.__threads:
            if (time.time() - starttime) > common.playlist_timeout:
                break
            thread.join(1)  
    
    @property
    def m3file(self):
        self.wait()
        m3file = model.M3U8()
        while True:
            try:
                playlist, headers = self.playlists.get(False)
                playlist.uri = encodeurl(url=playlist.absolute_uri, headers=headers)
                m3file.add_playlist(playlist)
            except Queue.Empty:
                break
        return m3file
    

def decodeurl(path):
    query = urlparse.urlparse(path)
    kwargs = dict(urlparse.parse_qsl(query.query))
    for kwarg in kwargs:
        kwargs[kwarg] = json.loads(urllib.unquote_plus(kwargs[kwarg]))
    return kwargs


def encodeurl(**kwargs):
    port = addon.kodisetting(common.addon_id).getstr("port")
    for kwarg in kwargs:
        kwargs[kwarg] = urllib.quote_plus(json.dumps(kwargs[kwarg]))
    return "http://localhost:%s/?%s" % (port, urllib.urlencode(kwargs))
