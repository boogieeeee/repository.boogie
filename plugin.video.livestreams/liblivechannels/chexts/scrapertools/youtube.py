try:
    import unittest
    import test

    class testyt(unittest.TestCase):
        def test_yt_link(self):
            test.testlink(self, itermedias("cnnturk", None), 1, "bein1", 0)

except ImportError:
    pass

import json
import re
import traceback
import htmlement

from tinyxbmc import net, mediaurl

ua = "Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36"


def getconsent(page):
    xpage = htmlement.fromstring(page)
    form = xpage.find(".//form")
    data = {}
    if form is None or "/save" not in form.get("action"):
        return page
    for inp in form.findall(".//input[@type='hidden']"):
        data[inp.get("name")] = inp.get("value")
    page = net.http(form.get("action"),
                    useragent=ua,
                    method="POST",
                    data=data)
    return page


def itermedias(youtube_chanid, youtube_sindex):
    try:
        u = "https://www.youtube.com/@%s/streams" % youtube_chanid
        page = getconsent(net.http(u, useragent=ua))
        t = re.search(r"ytInitialData\s*?=\s*?(?:\'|\")(.+)(?:\'|\");<\/script>", page)
        esc = t.group(1).encode().decode("unicode_escape")
        js = json.loads(esc)
        streams = []
        for tab in js["contents"].get("twoColumnBrowseResultsRenderer", js["contents"].get("singleColumnBrowseResultsRenderer"))["tabs"]:
            try:
                contents = tab["tabRenderer"]["content"]["richGridRenderer"]["contents"]
                for content in contents:
                    content = content["richItemRenderer"]["content"]
                    renderer = content.get("videoRenderer", content.get("compactVideoRenderer"))
                    streams.append(renderer["videoId"])
                break
            except KeyError:
                continue
        sindex = youtube_sindex if youtube_sindex is not None else 0
        vid = streams[sindex]
    except Exception:
        print(traceback.format_exc())
        return
    page = getconsent(net.http("https://www.youtube.com/watch?v=%s" % vid, useragent=ua))
    hls = re.search(r"hlsManifestUrl(?:\"|\')\s*?\:\s*?(?:\"|\')(.+?)(?:\"|\')", page).group(1)
    yield mediaurl.HlsUrl(hls, adaptive=True, ffmpegdirect=False)
