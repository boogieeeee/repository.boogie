'''
Created on Jan 31, 2020

@author: z0042jww
'''

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import socket


from thirdparty import m3u8
from tinyxbmc import net
from tinyxbmc import const

from liblivechannels import log
from liblivechannels import common
from liblivechannels import hls


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
                    component.uri = hls.encodeurl(url=component.absolute_uri, headers=headers)
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
        kwargs = hls.decodeurl(self.path)
        qurl = kwargs.get("url")
        qheaders = kwargs.get("headers")
        qplaylist = kwargs.get("playlist")
        qsegment_url = kwargs.get("segment_url")
        if qurl:
            self.proxy_handle(qurl, qheaders)
        elif qplaylist:
            chan = self.base.loadchannel(qplaylist)
            pgen = hls.PlaylistGenerator(self.base)
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
                    if self.base.resolve_mode in [0, 1]:
                        pgen.wait()
                        if pgen.playlists.qsize():
                            break
            self.wfile.write(pgen.m3file.dumps())
        elif qsegment_url:
            pass
        else:
            self.send_response(200)
            # self.send_header("Content-Type", "application/vnd.apple.mpegurl;charset=utf-8")
            self.end_headers()
            self.wfile.write('#EXTM3U\r\n')
            for icon, title, index, cats in self.base.channels.get("alives", []):
                surl = hls.encodeurl(playlist=index)
                for cat in cats:
                    descline = '#EXTINF:0 tvg-logo="%s" group-title="%s",%s\r\n' % (icon,
                                                                                    cat,
                                                                                    title)
                    self.wfile.write(descline.encode("utf-8"))
                    self.wfile.write('%s\r\n' % surl)

    @handle_client_disconnect
    def do_HEAD(self):
        kwargs = hls.decodeurl(self.path)
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
          