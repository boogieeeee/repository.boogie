'''
Created on Jan 31, 2020

@author: z0042jww
'''

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import urlparse
import urllib
import socket
import json
import threading
import Queue
import time

from thirdparty import m3u8
from thirdparty.m3u8 import model
from tinyxbmc import net
from tinyxbmc import const

from liblivechannels import log
from liblivechannels import common


logger = log.Logger()


def handle_client_disconnect(callback):
    def wrapper(*args, **kwargs):
        try:
            return callback(*args, **kwargs)
        except socket.error, e:
            if e.errno in [32, 104]:
                logger.info("Connection reset by peer: %s" % e.strerror)
            else:
                logger.error("%s: %s" % (e.strerror, e.errno))
                raise e
    return wrapper


class ThreadedProxy(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class Handler(BaseHTTPRequestHandler):
    def proxy_get(self, url, headers, send_response=True):
        if "user-agent" not in [x.lower() for x in headers.keys()]:
            headers[u"User-agent"] = const.USERAGENT
        try:
            resp = self.base.download(url, headers=headers, text=False,
                                      timeout=common.query_timeout, cache=None)
        except Exception, e:
            if send_response:
                self.send_response(500, str(e))
            return
        if send_response:
            self.send_response(resp.status_code)
            if resp.status_code == 200:
                self.end_headers()
                return resp.content
            else:
                return
        else:
            return resp.content

    def render_m3(self, content, url, headers):
        if content[:7] == "#EXTM3U":
            m3file = m3u8.loads(content, uri=url)
            for components in [m3file.playlists, m3file.segments, m3file.media]:
                for component in components:
                    component.uri = self.encodeurl(url=component.absolute_uri, headers=headers)
            return m3file

    def proxy_handle(self, url, headers):
        content = self.proxy_get(url, headers)
        if not content:
            return
        m3file = self.render_m3(content, url, headers)
        if m3file:
            self.wfile.write(m3file.dumps())
        else:
            self.wfile.write(content)

    @handle_client_disconnect
    def do_GET(self):
        kwargs = self.decodeurl(self.path)
        qurl = kwargs.get("url")
        qheaders = kwargs.get("headers")
        qplaylist = kwargs.get("playlist")
        qsegment_url = kwargs.get("segment_url")
        if qurl:
            self.proxy_handle(qurl, qheaders)
        elif qplaylist:
            chan = self.base.loadchannel(qplaylist)
            pgen = PlaylistGenerator(self)
            self.send_response(200)
            self.end_headers()
            for url in chan.get():
                url, headers = net.fromkodiurl(url)
                if not headers:
                    headers = {}
                content = self.proxy_get(url, headers, False)
                if not content:
                    continue
                if content[:7] == "#EXTM3U":
                    m3file = m3u8.loads(content, uri=url)
                    m3file.full_uri = url
                    pgen.add(m3file, headers)
            self.wfile.write(pgen.m3file.dumps())
        elif qsegment_url:
            pass
        else:
            self.send_response(200)
            # self.send_header("Content-Type", "application/vnd.apple.mpegurl;charset=utf-8")
            self.end_headers()
            self.wfile.write('#EXTM3U\r\n')
            for icon, title, index, cats in self.base.channels.get("alives", []):
                surl = self.encodeurl(playlist=index)
                for cat in cats:
                    descline = '#EXTINF:0 tvg-logo="%s" group-title="%s",%s\r\n' % (icon,
                                                                                    cat,
                                                                                    title)
                    self.wfile.write(descline.encode("utf-8"))
                    self.wfile.write('%s\r\n' % surl)

    @handle_client_disconnect
    def do_HEAD(self):
        kwargs = self.decodeurl(self.path)
        qurl = kwargs.get("url")
        qheaders = kwargs.get("headers", {})
        if qurl:
            resp = net.http(qurl, text=False, headers=qheaders, method="HEAD", timeout=common.query_timeout)
            self.send_response(resp.status_code)
        else:
            self.send_response(200)

    @handle_client_disconnect
    def finish(self):
        return BaseHTTPRequestHandler.finish(self)

    @handle_client_disconnect
    def handle(self):
        return BaseHTTPRequestHandler.handle(self)


    def decodeurl(self, path):
        query = urlparse.urlparse(path)
        kwargs = dict(urlparse.parse_qsl(query.query))
        for kwarg in kwargs:
            kwargs[kwarg] = json.loads(urllib.unquote_plus(kwargs[kwarg]))
        return kwargs
    
    
    def encodeurl(self, **kwargs):
        for kwarg in kwargs:
            kwargs[kwarg] = urllib.quote_plus(json.dumps(kwargs[kwarg]))
        return "http://localhost:%s/?%s" % (self.base.port, urllib.urlencode(kwargs))
    
    
class PlaylistGenerator(object):
    def __init__(self, handler):
        self.handler = handler
        self.playlists = Queue.Queue()
        self.__threads = []
        self.index = 10
       
    def add(self, m3file, headers):
        if len(m3file.playlists):
            for playlist in m3file.playlists:
                thread = threading.Thread(target=self.headcheck, args=(self.playlists, playlist, headers))
                thread.start()
                self.__threads.append(thread)
        elif len(m3file.segments):
            self.index += 1
            playlist = model.Playlist(m3file.full_uri,
                                      {"bandwidth": self.index},
                                      None, m3file.base_uri)
            self.playlists.put((playlist, headers))

    def headcheck(self, queue, playlist, headers):
        networkerr = False
        try:
            resp = self.handler.base.download(playlist.absolute_uri, headers=headers, method="HEAD",
                                              timeout=common.query_timeout)
        except Exception:
            networkerr = True
        if not networkerr and resp.status_code == 200:
            queue.put((playlist, headers))
        else:
            try:
                resp = self.handler.base.download(playlist.absolute_uri, headers=headers,
                                                  text=False, timeout=common.query_timeout)
            except Exception:
                return
            if resp.content[:7] == "#EXTM3U":
                queue.put((playlist, headers))
        pass
    
    @property
    def m3file(self):
        starttime = time.time()
        for thread in self.__threads:
            if (time.time() - starttime) > common.playlist_timeout:
                break
            thread.join(1)
        m3file = m3u8.M3U8()
        while True:
            try:
                playlist, headers = self.playlists.get(False)
                playlist.uri = self.handler.encodeurl(url=playlist.absolute_uri, headers=headers)
                m3file.add_playlist(playlist)
            except Queue.Empty:
                break
        return m3file
            