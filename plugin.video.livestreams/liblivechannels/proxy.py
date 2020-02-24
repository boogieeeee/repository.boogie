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

from thirdparty import m3u8
from tinyxbmc import net
from tinyxbmc import const

import liblivechannels
from liblivechannels import log

from addon import Base
import common

logger = log.Logger()
base = Base(addon=common.addon_id)


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
    def proxy_get(self, url, headers):
        if "user-agent" not in [x.lower() for x in headers.keys()]:
            headers[u"User-agent"] = const.USERAGENT
        resp = base.download(url, headers=headers, text=False)
        self.send_response(resp.status_code)
        if resp.status_code == 200:
            self.end_headers()
            return resp.content
        else:
            return

    def render_m3(self, content, url, headers):
        if content[:7] == "#EXTM3U":
            m3file = m3u8.loads(content, uri=url)
            for components in [m3file.playlists, m3file.segments, m3file.media]:
                for component in components:
                    component.uri = encodeurl(url=component.absolute_uri, headers=headers)
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
        kwargs = decodeurl(self.path)
        qurl = kwargs.get("url")
        qheaders = kwargs.get("headers")
        qplaylist = kwargs.get("playlist")
        if qurl:
            self.proxy_handle(qurl, qheaders)
        elif qplaylist:
            chan = liblivechannels.loadchannel(qplaylist, base.download)
            for url in chan.get():
                url, headers = net.fromkodiurl(url)
                if not headers:
                    headers = {}
                self.proxy_handle(url, headers)
                # TODO: merge all variants
                break
        else:
            self.send_response(200)
            # self.send_header("Content-Type", "application/vnd.apple.mpegurl;charset=utf-8")
            self.end_headers()
            self.wfile.write('#EXTM3U\r\n')
            for icon, title, index, cats in base.channels.get("alives", []):
                surl = encodeurl(playlist=index)
                for cat in cats:
                    descline = '#EXTINF:0 tvg-logo="%s" group-title="%s",%s\r\n' % (icon,
                                                                                    cat,
                                                                                    title)
                    self.wfile.write(descline.encode("utf-8"))
                    self.wfile.write('%s\r\n' % surl)

    @handle_client_disconnect
    def do_HEAD(self):
        qurl, qheaders = decodeurl(self.path)
        resp = net.http(qurl, text=False, headers=qheaders, method="HEAD")
        self.send_response(resp.status_code)

    @handle_client_disconnect
    def finish(self):
        return BaseHTTPRequestHandler.finish(self)

    @handle_client_disconnect
    def handle(self):
        return BaseHTTPRequestHandler.handle(self)


def decodeurl(path):
    query = urlparse.urlparse(path)
    kwargs = dict(urlparse.parse_qsl(query.query))
    for kwarg in kwargs:
        kwargs[kwarg] = json.loads(urllib.unquote_plus(kwargs[kwarg]))
    return kwargs


def encodeurl(**kwargs):
    for kwarg in kwargs:
        kwargs[kwarg] = urllib.quote_plus(json.dumps(kwargs[kwarg]))
    return "http://localhost:8000/?%s" % urllib.urlencode(kwargs)
