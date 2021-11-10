import json
import re
import traceback
import random

from tinyxbmc import net

ua = "Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36"

COOKIE = 'CONSENT=YES+cb-m.20210328-17-p0.en+FX+%s' % random.randint(100, 999)


def itermedias(youtube_chanid, youtube_stream, youtube_sindex):
    try:
        u = "https://m.youtube.com/%s/videos?view=2&flow=list&live_view=501&" % youtube_chanid
        page = net.http(u,
                        useragent=ua,
                        headers={"Cookie": COOKIE})
        try:
            js = json.loads(re.search('<div id="initial-data"><!-- (.+?) -->', page).group(1))
        except AttributeError:
            t = re.search("ytInitialData = '(.+?)'", page).group(1)
            js = json.loads(t.encode("utf-8").decode("unicode-escape"))
        streams = js["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][1]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
        sindex = None

        if youtube_stream:
            for sindex, stream in enumerate(streams):
                if youtube_stream(stream):
                    break

        if not sindex and youtube_sindex:
            sindex = youtube_sindex

        if sindex is None:
            sindex = 0
        vid = streams[sindex]["compactVideoRenderer"]["videoId"]
        # icon = js["metadata"]["channelMetadataRenderer"]["avatar"]["thumbnails"][0]["url"]
    except Exception:
        print(traceback.format_exc())
        return
    page = net.http("https://m.youtube.com/watch?v=%s" % vid,
                    useragent=ua,
                    headers={"Cookie": COOKIE})
    pconfig1 = re.search('ytInitialPlayerConfig = (\{.+?\})\;', page)
    if pconfig1:
        js = json.loads(pconfig1.group(1))
        response = json.loads(js["args"]["player_response"])
    else:
        response = json.loads(re.search('ytInitialPlayerResponse\s*?\=\s*?(\{.+?\})\;', page).group(1))
    # dash = response["streamingData"].get("dashManifestUrl")
    # if dash:
    #     yield net.mpdurl(dash)
    yield net.hlsurl(response["streamingData"]["hlsManifestUrl"])
