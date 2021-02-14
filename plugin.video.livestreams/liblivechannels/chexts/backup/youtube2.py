# -*- encoding: utf-8 -*-
from liblivechannels import scrapers, scraper

import re
import json
import traceback

from scrapertools import yayinakisi


def istv100(stream):
    return "ekonomi" not in stream["compactVideoRenderer"]["title"]["runs"][0]["text"].lower()


channels = {u"Haber Türk": {"cid": "haberturktv", "cats": [u"Türkçe", u"Haber"]},
            u"CNN Türk": {"cid": "cnnturk", "cats": [u"Türkçe", u"Haber"]},
            u"Bloomberg HT": {"cid": "bloomberght", "cats": [u"Türkçe", u"Haber"]},
            u"Show TV": {"cid": "ShowTV", "cats": [u"Türkçe", u"Realiti"]},
            u"Tele 1": {"cid": "Tele1comtr", "cats": [u"Türkçe", u"Haber"]},
            u"NTV": {"cid": "NTV", "cats": [u"Türkçe", u"Haber"]},
            u"A Haber": {"cid": "ahaber", "cats": [u"Türkçe", u"Haber"]},
            u"Halk TV": {"cid": "Halktvkanali", "cats": [u"Türkçe", u"Haber"]},
            u"Haber Global": {"cid": "haberglobal", "cats": [u"Türkçe", u"Haber"]},
            u"TV100": {"cid": "tv100", "isvalid": istv100, "cats": [u"Türkçe", u"Haber"]},
            u"TGRT Haber": {"cid": "tgrthaber", "cats": [u"Türkçe", u"Haber"]},
            u"TRT Haber": {"cid": "trthaber", "cats": [u"Türkçe", u"Haber"]},
            # u"A Spor": {"cid": "ASpor", "cats": [u"Türkçe", u"Haber"]},
            # u"TV 2": {"cid": "tv2tv", "cats": [u"Türkçe", u"Haber"]},
            u"Ulusal Kanal": {"cid": "UlusalKanalTV", "cats": [u"Türkçe", u"Haber"]},
            u"TV Net": {"cid": "tvnet", "cats": [u"Türkçe", u"Haber"]},
            u"LoFi Channel 1": {"cid": "ChilledCow", "cats": [u"Music"]},
            u"LoFi Channel 2": {"cid": "ChilledCow", "streamindex": 1, "cats": [u"Music"]}
            }

ua = "Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36"


class chan(object):
    subchannel = True
    vid = None
    usehlsproxy = False

    def get(self):
        page = self.download("https://www.youtube.com/watch?v=%s" % self.vid,
                             useragent=ua,
                             headers={"Cookie": "GPS=1"})
        pconfig1 = re.search('ytInitialPlayerConfig = (\{.+?\})\;', page)
        if pconfig1:
            js = json.loads(pconfig1.group(1))
            response = json.loads(js["args"]["player_response"])
        else:
            response = json.loads(re.search('ytInitialPlayerResponse\s*?\=\s*?(\{.+?\})\;', page).group(1))
        yield response["streamingData"]["hlsManifestUrl"]

    def iterprogrammes(self):
        for prog in yayinakisi.iterprogramme(self.title):
            yield prog


class youtube(object):
    def iteratechannels(self):
        for title, channel in channels.iteritems():
            try:
                page = self.download("https://m.youtube.com/c/%s/videos?view=2&flow=list&live_view=501&" % channel["cid"],
                                     useragent=ua,
                                     headers={"Cookie": "GPS=1"})
                try:
                    js = json.loads(re.search('<div id="initial-data"><!-- (.+?) -->', page).group(1))
                except AttributeError:
                    t = re.search("ytInitialData = '(.+?)'", page).group(1)
                    js = json.loads(t.encode("utf-8").decode("string-escape"))
                streams = js["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][1]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
                sindex = None

                if channel.get("isvalid"):
                    for sindex, stream in enumerate(streams):
                        if channel["isvalid"](stream):
                            break

                if not sindex and channel.get("streamindex"):
                    sindex = channel["streamindex"]

                if sindex is None:
                    sindex = 0
                vid = streams[sindex]["compactVideoRenderer"]["videoId"]
                icon = js["metadata"]["channelMetadataRenderer"]["avatar"]["thumbnails"][0]["url"]
            except Exception:
                print channel
                print traceback.format_exc()
                continue
            cid = json.dumps([vid, title])
            yield self.makechannel(cid, chan, vid=vid, title=title, icon=icon, categories=["youtube"] + channel["cats"])

    def getchannel(self, cid):
        vid, title = json.loads(cid)
        return self.makechannel(cid, chan, vid=vid, title=title)
