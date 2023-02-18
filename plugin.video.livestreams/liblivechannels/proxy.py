'''
Created on Jan 31, 2020

@author: z0042jww
'''
from six.moves.BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from six.moves.socketserver import ThreadingMixIn

import socket
import re
import binascii
import base64

from thirdparty import m3u8
from tinyxbmc import net
from tinyxbmc import mediaurl
from tinyxbmc import tools
from tinyxbmc import const

from liblivechannels import log
from liblivechannels import hls
from liblivechannels import epg
from liblivechannels import common


logger = log.Logger()


def handle_client_disconnect(callback):
    def wrapper(*args, **kwargs):
        try:
            return callback(*args, **kwargs)
        except socket.error as e:
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
        self.wfile.write("\r\n".encode())

    def render_m3(self, resp, url, headers):
        try:
            header = resp.content[:7]
        except Exception as e:
            return e
        if header in ("#EXTM3U", b"#EXTM3U"):
            m3file = m3u8.loads(resp.content.decode(), uri=url)
            for components in [m3file.playlists, m3file.segments, m3file.media]:
                for component in components:
                    key = iv = method = None
                    if hasattr(component, "key") and component.key and component.key.uri:
                        if not component.key.uri.startswith("http"):
                            component.key.uri = m3file.base_uri + component.key.uri
                        if not component.key.uri.startswith("http://localhost"):  # always routes key uri through proxy but thats ok.
                            component.key.uri = hls.encodeurl(url=component.key.uri, headers=headers)
                        elif component.key.iv and "base64," in component.key.uri:
                            key = binascii.hexlify(base64.b64decode(re.search("base64,(.+)", component.key.uri).group(1))).decode()
                            iv = component.key.iv[2:]
                            method = component.key.method
                            component.key = None
                    component.uri = hls.encodeurl(url=component.absolute_uri, headers=headers, encryption={"key": key, "iv": iv, "method": method})
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
            resp = self.base.http_retry(qurl, qheaders)
            if isinstance(resp, Exception) or resp is None:
                self.send_response(500, str(resp))
                self.end_headers()
            else:
                m3file = self.render_m3(resp, qurl, qheaders)
                if isinstance(m3file, Exception):
                    self.send_response(500, str(m3file))
                    return
                self.send_response(resp.status_code)
                self.end_headers()
                if m3file:
                    self.wfile.write(m3file.dumps().encode())
                else:
                    decryptor = hls.DecryptPayload(**kwargs.get("encryption", {}))
                    for chunk in resp.iter_content(decryptor.chunksize, False):
                        data = decryptor.decrypt(chunk)
                        self.wfile.write(data)
                    self.wfile.write(decryptor.flush())
        elif qplaylist:
            chan = self.base.loadchannel(qplaylist)
            if not chan:
                return
            pgen = hls.PlaylistGenerator(self.base)
            for url in tools.safeiter(chan.get()):
                if isinstance(url, mediaurl.mpdurl) and url.inputstream:
                    pass
                    # skip mpds for now, partly broken
                elif isinstance(url, mediaurl.acestreamurl):
                    # todo: check if ffmpegdirect is the player
                    if self.base.check_acestreamurl(url)[0] is None:
                        self.send_response(301)
                        self.send_header('Location', url.kodiurl)
                    else:
                        self.send_response(500)
                    self.end_headers()
                    break
                else:
                    error, resp, headers = self.base.check_hlsurl(url)
                    print(error, resp, headers)
                    if error is None:
                        self.send_response(200)
                        self.end_headers()
                        content = resp.content.decode()
                        print(content, resp.url)
                        m3file = m3u8.loads(content, uri=resp.url)
                        m3file.full_uri = resp.url
                        print(m3file)
                        pgen.add(m3file, headers)
                        if pgen.playlists.qsize():
                            print(1121)
                            self.wfile.write(pgen.m3file.dumps().encode())
                            break
        elif qepg:  # epg response
            self.send_response(200)
            self.end_headers()
            epg.write(self.base).start()
            self.writeline(common.epath)
        else:  # main channel list
            self.send_response(200)
            # self.send_header("Content-Type", "application/vnd.apple.mpegurl;charset=utf-8")
            self.end_headers()
            self.writeline('#EXTM3U')
            playlists = self.base.config.playlists
            for icon, title, index, cats, url in self.base.config.channels:
                pnames = []
                for playlistname, indexes in self.base.config.iterplaylists(playlists):
                    if index in indexes:
                        pnames.append(playlistname)
                playlisturl = None
                if url:
                    if self.base.config.ffmpegdirect:
                        self.writeline("#KODIPROP:inputstreamaddon=inputstream.ffmpegdirect")
                        self.writeline("#KODIPROP:inputstreamclass=inputstream.ffmpegdirect")
                        self.writeline("#KODIPROP:inputstream.ffmpegdirect.stream_mode=timeshift")
                        self.writeline("#KODIPROP:inputstream.ffmpegdirect.is_realtime_stream=false")
                        # self.writeline("#KODIPROP:inputstream.ffmpegdirect.manifest_type=hls")
                    elif url.inputstream:
                        self.writeline("#KODIPROP:inputstreamaddon=inputstream.adaptive")
                        self.writeline("#KODIPROP:inputstreamclass=inputstream.adaptive")
                        self.writeline("#KODIPROP:inputstream.adaptive.manifest_type=%s" % url.manifest)
                        if isinstance(url, mediaurl.mpdurl):
                            if url.lurl:
                                self.writeline('#KODIPROP:inputstream.adaptive.license_type=%s' % url.license)
                                url.lurl, url.lheaders = net.fromkodiurl(net.tokodiurl(url.lurl, headers=url.lheaders, pushua=const.USERAGENT, pushverify="false"))
                                self.writeline('#KODIPROP:inputstream.adaptive.license_key=%s' % url.kodilurl)
                            playlisturl = net.tokodiurl(url.url, headers=url.headers, pushverify="false", pushua=const.USERAGENT)
                        self.writeline("#KODIPROP:inputstream.adaptive.stream_headers=%s" % const.USERAGENT)
                self.writeline('#EXTINF:0 tvg-logo="%s" tvg-id="%s" group-title="%s",%s' % (icon,
                                                                                            index,
                                                                                            ";".join(cats + pnames),
                                                                                            title))
                self.writeline(playlisturl or hls.encodeurl(playlist=index))

    @handle_client_disconnect
    def do_HEAD(self):
        kwargs = hls.decodeurl(self.path)
        qurl = kwargs.get("url")
        qheaders = kwargs.get("headers", {})
        if qurl:
            resp = self.base.http_retry(qurl, qheaders, method="HEAD")
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
