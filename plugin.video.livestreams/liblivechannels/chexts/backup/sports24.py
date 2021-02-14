from liblivechannels import scrapers, scraper
from liblivechannels import config

from tinyxbmc import net
from tinyxbmc import tools

import re
import htmlement
import json

domain = config.config().sports24
baseurl = net.absurl("/tv", domain)


class chan(scraper):
    subchannel = True
    url = None
    categories = ["Sports24"]
    xpage = None

    def get(self):
        if not self.xpage:
            self.xpage = htmlement.fromstring(self.download(self.url, referer=baseurl))
        for iframe in self.xpage.iterfind(".//iframe"):
            iframeurl = iframe.get("src")
            if iframeurl:
                iframeurl = net.absurl(iframeurl, self.url)
                if "/tv/embed" in iframeurl:
                    iframesrc = self.download(iframeurl, referer=self.url)
                    url = re.search("atob\(\'(.+?)\'\)", iframesrc)
                    if url:
                        yield net.absurl(url.group(1).decode("base64"), iframeurl)
                    break
                elif "/bm/play.php" in iframeurl:
                    iframesrc = self.download(iframeurl, referer=self.url)
                    mpd = re.search('var src = "(.+?)"', iframesrc)
                    mpdlic = re.search('var myWV = "(.+?)"', iframesrc)
                    headers = {"Referer": iframeurl}
                    if mpd and mpdlic:
                        mpd = net.absurl(mpd.group(1), iframeurl)
                        mpdlic = net.absurl(mpdlic.group(1), iframeurl)
                        yield net.mpdurl(mpd, headers, mpdlic, headers)
                    break


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
        print re.search("var _0x4f04=(\[\'.+?\'\])", subpage).group(1)
        jslist = eval(re.search("var _0x4f04=(\[\'.+?\'\])", subpage).group(1))
        cid = "".join((jslist[210], jslist[216], jslist[14])) + re.findall("\+'([a-fA-F0-9]{2})'", subpage)[1]
        uid = "".join((jslist[128], jslist[186], jslist[183], jslist[115])) 
        body = '{"env":"production","user_id":"%s","channel_id":"%s","message":[D{SSM}]}' % (uid, cid)
        mpd = self.js["playback_info"]["dash_manifest_url"].replace("http://", "https://")
        print guid
        print cid
        print uid
        print body
        yield net.mpdurl(mpd, headers, mpdl, headers, lbody=body)


class sports24(scrapers):
    def iteratechannels(self):
        xpage = htmlement.fromstring(self.download(baseurl))
        for a in xpage.iterfind(".//div[@id='myTable']/a"):
            churl = net.absurl(a.get("href"), baseurl)
            yield self.makechannel(churl, chan, url=churl, title=a.text)

    def getchannel(self, url):
        xpage = htmlement.fromstring(self.download(url, referer=baseurl))
        title = tools.elementsrc(xpage.find(".//div[@id='gamecard']"))
        return self.makechannel(url, chan, url=url, title=title, xpage=xpage)


class sports24js():
    def iteratechannels(self):
        for channel in self.download(net.absurl("/bm/channels.json", domain), referer=domain, json=True):
            url = channel["qvt"]
            yield self.makechannel(url, chanjs,
                                   title=channel["title"],
                                   icon=channel["image"]["url"],
                                   url=url
                                   )

    def getchannel(self, url):
        js = self.download(url, referer=domain, json=True)
        return self.makechannel(url, chanjs,
                                url=url,
                                js=js)
