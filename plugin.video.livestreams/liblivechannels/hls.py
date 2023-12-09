import json

from six.moves.urllib import parse
from six.moves import queue

from liblivechannels import common
from thirdparty.m3u8 import model

from tinyxbmc import addon
from tinyxbmc import mediaurl

import subprocess


class PlaylistGenerator(object):
    def __init__(self, base):
        self.base = base
        self.playlists = queue.Queue()
        self.index = 10

    @staticmethod
    def sorter(playlist):
        return playlist.stream_info.bandwidth

    def add(self, m3file, headers):
        if len(m3file.playlists):
            for playlist in sorted(m3file.playlists, key=self.sorter, reverse=True):
                self.headcheck(playlist, headers)
                if self.playlists.qsize():
                    break
        elif len(m3file.segments):
            m3file.full_uri = encodeurl(url=m3file.full_uri, headers=headers)
            self.index += 1
            playlist = model.Playlist(m3file.full_uri,
                                      {"bandwidth": self.index},
                                      None, m3file.base_uri)
            self.playlists.put(playlist)

    def headcheck(self, playlist, headers):
        error, _resp, _headers = self.base.healthcheck(mediaurl.hlsurl(playlist.absolute_uri, headers=headers))
        if error is None:
            playlist.uri = encodeurl(url=playlist.absolute_uri, headers=headers)
            self.playlists.put(playlist)

    @property
    def m3file(self):
        m3file = model.M3U8()
        while True:
            try:
                m3file.add_playlist(self.playlists.get(False))
            except queue.Empty:
                break
        return m3file


def decodeurl(path):
    query = parse.urlparse(path)
    kwargs = dict(parse.parse_qsl(query.query))
    for kwarg in kwargs:
        kwargs[kwarg] = json.loads(parse.unquote_plus(kwargs[kwarg]))
    return kwargs


def encodeurl(**kwargs):
    port = addon.kodisetting(common.addon_id).getstr("port")
    for kwarg in kwargs:
        kwargs[kwarg] = parse.quote_plus(json.dumps(kwargs[kwarg]))
    return "http://localhost:%s/?%s" % (port, parse.urlencode(kwargs))


class DecryptPayload:
    try:
        hasopenssl = subprocess.Popen(["openssl", "version"],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT).wait()
        hasopenssl = hasopenssl == 0
    except Exception:
        hasopenssl = False

    def __init__(self, method=None, key=None, iv=None):
        self.aes = None
        self.key = key
        self.method = method
        self.iv = iv
        self.chunksize = None
        self.skipdec = method not in ["AES-128"]

    def decrypt(self, chunk):
        if self.skipdec:
            return chunk
        elif self.hasopenssl:
            prc = subprocess.Popen(["openssl", "enc", "-d", "-aes-128-cbc", "-K", self.key, "-iv", self.iv],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            return prc.communicate(chunk)[0]

    def flush(self):
        return b""
