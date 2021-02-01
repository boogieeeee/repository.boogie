import threading
import Queue
import time
import urlparse
import urllib
import json

from liblivechannels import common
from thirdparty.m3u8 import model

from tinyxbmc import addon
from tinyxbmc import net


class MPDPlaylist(model.Playlist):
    def __init__(self, mpd, *args, **kwargs):
        super(MPDPlaylist, self).__init__(mpd.url, *args, **kwargs)
        self.props = "#KODIPROP:inputstream=%s\n" % mpd.inputstream
        # self.props += "#KODIPROP:inputstreamclass=%s\n" % mpd.inputstream
        self.props += "#KODIPROP:inputstream=%s\n" % mpd.inputstream
        self.props += "#KODIPROP:mimetype=application/dash+xml\n"
        # self.props += "#KODIPROP:inputstream.adaptive.mimetype=application/dash+xml\n"
        self.props += "#KODIPROP:inputstream.adaptive.manifest_type=%s\n" % mpd.manifest
        if mpd.lurl:
            self.props += "#KODIPROP:inputstream.adaptive.license_type=%s\n" % mpd.license
            self.props += "#KODIPROP:inputstream.adaptive.license_key=%s" % mpd.kodilurl
        self.uri = mpd.kodiurl

    def __str__(self):
        return "#EXTINF:-1,MyChannel\n" + "/home/boogie/test.strm"


class PlaylistGenerator(object):
    def __init__(self, base):
        self.base = base
        self.playlists = Queue.Queue()
        self.__threads = []
        self.index = 10

    @staticmethod
    def sorter(playlist):
        return playlist.stream_info.bandwidth

    def add(self, m3file, headers, pltype="hlsproxy"):
        if pltype == "mpd":
            self.playlists.put((MPDPlaylist(m3file,
                                            {"bandwidth": self.index},
                                            None,
                                            m3file.url), headers), pltype)
        elif len(m3file.playlists):
            for playlist in sorted(m3file.playlists, key=self.sorter, reverse=True):
                if self.base.config.resolve_mode == 0 and pltype == "hlsproxy":
                    self.headcheck(playlist, headers, pltype)
                    if self.playlists.qsize():
                        break
                else:
                    thread = threading.Thread(target=self.headcheck, args=(playlist, headers, pltype))
                    thread.start()
                    self.__threads.append(thread)
        elif len(m3file.segments):
            if pltype == "hls":
                m3file.full_uri = net.tokodiurl(m3file.full_uri, headers=headers)
            self.index += 1
            playlist = model.Playlist(m3file.full_uri,
                                      {"bandwidth": self.index},
                                      None, m3file.base_uri)
            self.playlists.put((playlist, headers, pltype))

    def headcheck(self, playlist, headers, pltype):
        if pltype == "hls":
            playlist.uri = net.tokodiurl(playlist.absolute_uri, headers=headers)
            error = None
        else:
            error = self.base.healthcheck(playlist.absolute_uri, headers)
        if error is None:
            self.playlists.put((playlist, headers, pltype))

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
                playlist, headers, pltype = self.playlists.get(False)
                if pltype == "hlsproxy":
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
