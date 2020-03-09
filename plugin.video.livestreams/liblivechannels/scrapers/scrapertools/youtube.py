import sys
import datetime
import ghub
import time
import urllib


def proxyisatty():
    return False


class proxydt(datetime.datetime):
    def __init__(self, *args, **kwargs):
        super(proxydt, self).__init__(*args, **kwargs)

    @staticmethod
    def strptime(date_string, fmt):
        return datetime.datetime(*(time.strptime(date_string, fmt)[0:6]))


class ydl(object):
    title = "Youtube DL Link Extension"

    def __init__(self, isyoutube=True):
        sys.stderr.isatty = proxyisatty
        datetime.datetime = proxydt
        uname = "ytdl-org"
        branch = "master"
        commit = None
        ghub.load(uname, "youtube-dl", branch, commit)
        import youtube_dl as ydl
        self.ydl = ydl
        if isyoutube:
            from youtube_dl.extractor import YoutubeIE, YoutubeLiveIE
            self.ies = [YoutubeIE(), YoutubeLiveIE()]
        else:
            self.ies = ydl.extractor.gen_extractors()

    def getresults(self, result):
        headers = result.get("http_headers", {})
        headers["Referer"] = result.get("webpage_url", "")
        suffix = "|" + urllib.urlencode(headers)
        for k in ('entries', "requested_formats"):
            if k in result:
                # Can be a playlist or a list of videos
                for res in result[k]:
                    if "url" in res:
                        yield res["url"] + suffix
        if "url" in result:
            # Just a video
            yield result["url"] + suffix

    def geturls(self, link, headers=None):
        if "youtube" in link or "youtu.be" in link:
            supported = False
            for ie in self.ies:
                if ie.suitable(link) and ie.IE_NAME != 'generic':
                    supported = True
                    break
            if not supported:
                yield
            ytb = self.ydl.YoutubeDL({'format': 'bestvideo+bestaudio/best',
                                      "quiet": True,
                                      "nocheckcertificate": True})
            ytb._ies = [ie]
            with ytb:
                result = ytb.extract_info(str(link), download=False)

            for url in self.getresults(result):
                yield url
