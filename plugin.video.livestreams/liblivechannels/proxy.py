'''
Created on Jan 31, 2020

@author: z0042jww
'''

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import socket


from thirdparty import m3u8
from tinyxbmc import net
from tinyxbmc import tools

from liblivechannels import log
from liblivechannels import hls
from liblivechannels import epg
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
    def writeline(self, txt):
        self.wfile.write(txt.encode("utf-8"))
        self.wfile.write("\r\n")

    def render_m3(self, content, url, headers):
        if content[:7] == "#EXTM3U":
            m3file = m3u8.loads(content, uri=url)
            for components in [m3file.playlists, m3file.segments, m3file.media]:
                for component in components:
                    component.uri = hls.encodeurl(url=component.absolute_uri, headers=headers)
            return m3file

    @handle_client_disconnect
    def do_GET(self):
        kwargs = hls.decodeurl(self.path)
        qurl = kwargs.get("url")
        qheaders = kwargs.get("headers", {})
        qplaylist = kwargs.get("playlist")
        qepg = kwargs.get("epg")
        if qurl:
            rng = self.headers.get("Range")
            if rng:
                qheaders["Range"] = rng
            resp = self.base.proxy_get(qurl, qheaders)
            if isinstance(resp, Exception) or resp is None:
                self.send_response(500, str(resp))
                self.end_headers()
            else:
                self.send_response(resp.status_code)
                self.end_headers()
                m3file = self.render_m3(resp.content, qurl, qheaders)
                if m3file:
                    self.wfile.write(m3file.dumps())
                else:
                    self.wfile.write(resp.content)
        elif qplaylist:
            chan = self.base.loadchannel(qplaylist)
            if not chan:
                return
            pgen = hls.PlaylistGenerator(self.base)
            self.send_response(200)
            self.end_headers()
            for url in tools.safeiter(chan.get()):
                url, headers = net.fromkodiurl(url)
                if not headers:
                    headers = {}
                resp = self.base.proxy_get(url, headers)
                if resp is not None and not isinstance(resp, Exception):
                    if resp.content[:7] == "#EXTM3U":
                        m3file = m3u8.loads(resp.content, uri=url)
                        m3file.full_uri = url
                        pgen.add(m3file, headers)
                        if self.base.config.resolve_mode in [0, 1]:
                            pgen.wait()
                            if pgen.playlists.qsize():
                                break
            self.wfile.write(pgen.m3file.dumps())
        elif qepg:
            self.send_response(200)
            self.end_headers()
            epg.write(self.base).start()
            self.writeline(common.epath)
        else:
            self.send_response(200)
            # self.send_header("Content-Type", "application/vnd.apple.mpegurl;charset=utf-8")
            self.end_headers()
            self.writeline('#EXTM3U')
            playlists = self.base.config.playlists
            for icon, title, index, cats in self.base.config.channels:
                pnames = []
                for playlistname, indexes in self.base.config.iterplaylists(playlists):
                    if index in indexes:
                        pnames.append(playlistname)
                self.writeline('#EXTINF:0 tvg-logo="%s" tvg-id="%s" group-title="%s",%s' % (icon,
                                                                                            index,
                                                                                            ";".join(cats + pnames),
                                                                                            title))
                self.writeline(hls.encodeurl(playlist=index))

    @handle_client_disconnect
    def do_HEAD(self):
        kwargs = hls.decodeurl(self.path)
        qurl = kwargs.get("url")
        qheaders = kwargs.get("headers", {})
        if qurl:
            resp = self.base.proxy_get(qurl, qheaders, method="HEAD")
            if isinstance(resp, Exception) or resp is None:
                self.send_response(500, str(resp))
            else:
                self.send_response(resp.status_code)
            self.end_headers()
        else:
            self.send_response(200)

    @handle_client_disconnect
    def finish(self):
        return BaseHTTPRequestHandler.finish(self)

    @handle_client_disconnect
    def handle(self):
        return BaseHTTPRequestHandler.handle(self)
