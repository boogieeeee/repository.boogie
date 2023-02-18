from liblivechannels import scraper
from tinyxbmc import net, mediaurl
import base64

import re


domain = "https://sports24.stream"


def itermedias(chid):
    iframeurl = "%s/bm/vid.php?id=%s" % (domain, chid)
    iframesrc = net.http(iframeurl, referer=domain)
    mpd = re.search('var src = "(.+?)"', iframesrc)
    mpdlic = re.search('var myWV = "(.+?)"', iframesrc)
    headers = {"Referer": iframeurl}
    if mpd and mpdlic:
        mpd = net.absurl(base64.b64decode(mpd.group(1)).decode(), iframeurl)
        mpdlic = net.absurl(base64.b64decode(mpdlic.group(1)).decode(), iframeurl)
        m = mediaurl.mpdurl(mpd, headers, mpdlic, headers.copy())
        yield m


class chanjs(scraper):
    subchannel = True
    url = None
    categories = []
    title = "JSchan"
    js = None

    def get(self):
        if not self.js:
            self.js = self.download(self.url, referer=domain, json=True)
        guid = self.js["playback_info"]["linear_info"]["channel_guid"]
        suburl = "%s/bm/sl.php?ch=%s" % (domain, guid)
        subpage = self.download(suburl, referer=domain)
        mpdl = re.search('myWV = "(.+?)"', subpage).group(1)
        headers = {"Referer": suburl}
        print(re.search("var _0x4f04=(\[\'.+?\'\])", subpage).group(1))
        jslist = eval(re.search("var _0x4f04=(\[\'.+?\'\])", subpage).group(1))
        cid = "".join((jslist[210], jslist[216], jslist[14])) + re.findall("\+'([a-fA-F0-9]{2})'", subpage)[1]
        uid = "".join((jslist[128], jslist[186], jslist[183], jslist[115]))
        body = '{"env":"production","user_id":"%s","channel_id":"%s","message":[D{SSM}]}' % (uid, cid)
        mpd = self.js["playback_info"]["dash_manifest_url"].replace("http://", "https://")
        print(guid)
        print(cid)
        print(uid)
        print(body)
        yield mediaurl.mpdurl(mpd, headers, mpdl, headers, lbody=body)


class sports24js():
    def iteratechannels(self):
        for channel in self.download(net.absurl("/bm/channels.json", domain), referer=domain, json=True):
            url = channel["qvt"]
            img = channel.get("image")
            if img:
                img = img.get("url", "DefaultFodler.png")
            else:
                img = "DefaultFolder.png"
            yield self.makechannel(url, chanjs,
                                   title=channel["title"],
                                   icon=img,
                                   url=url
                                   )

    def getchannel(self, url):
        js = self.download(url, referer=domain, json=True)
        return self.makechannel(url, chanjs,
                                url=url,
                                js=js)
