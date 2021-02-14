import json
import re
import traceback


ua = "Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36"


class youtube(object):
    youtube_stream = None
    youtube_sindex = None

    def iteryoutube(self):
        try:
            page = self.download("https://m.youtube.com/c/%s/videos?view=2&flow=list&live_view=501&" % self.youtube_chanid,
                                 useragent=ua,
                                 headers={"Cookie": "GPS=1"})
            try:
                js = json.loads(re.search('<div id="initial-data"><!-- (.+?) -->', page).group(1))
            except AttributeError:
                t = re.search("ytInitialData = '(.+?)'", page).group(1)
                js = json.loads(t.encode("utf-8").decode("string-escape"))
            streams = js["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][1]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
            sindex = None

            if self.youtube_stream:
                for sindex, stream in enumerate(streams):
                    if self.youtube_stream(stream):
                        break

            if not sindex and self.youtube_sindex:
                sindex = self.youtube_sindex

            if sindex is None:
                sindex = 0
            vid = streams[sindex]["compactVideoRenderer"]["videoId"]
            # icon = js["metadata"]["channelMetadataRenderer"]["avatar"]["thumbnails"][0]["url"]
        except Exception:
            print traceback.format_exc()
            return
        page = self.download("https://www.youtube.com/watch?v=%s" % vid,
                             useragent=ua,
                             headers={"Cookie": "GPS=1"})
        pconfig1 = re.search('ytInitialPlayerConfig = (\{.+?\})\;', page)
        if pconfig1:
            js = json.loads(pconfig1.group(1))
            response = json.loads(js["args"]["player_response"])
        else:
            response = json.loads(re.search('ytInitialPlayerResponse\s*?\=\s*?(\{.+?\})\;', page).group(1))
        yield response["streamingData"]["hlsManifestUrl"]
