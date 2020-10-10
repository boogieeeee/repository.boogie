from liblivechannels import scrapers, scraper
from liblivechannels import config

from tinyxbmc import net

import re
import htmlement

cfg = config.config()


class chan(scraper):
    subchannel = True
    cpage = None

    def get(self):
        player = self.cpage.find('.//div[@class="live-player"]')
        loadbalancer = player.get("data-loadbalancerdomain")
        loadbalancerdata = player.get("data-loadbalancer")
        try:
            data_d = self.cpage.find(".//body").get("data-d")
        except Exception:
            data_d = "d"
        try:
            url = self.cpage.find(".//meta[@name='rd']").get("content")
        except Exception:
            url = "https://check.nlivecdn.com"
        url = "%s/%s/%s/%s/%s/1" % (url,
                                    data_d,
                                    loadbalancerdata,
                                    self.datastream,
                                    loadbalancer,
                                    )
        link = net.tokodiurl(url, None, {"referer": cfg.cdnlive + "/",
                                         "Origin": cfg.cdnlive})
        yield link


class cdnlive(scrapers):
    def getitems(self, url):
        # find the domain name automatically, this domain keeps changing
        xpath = ".//div[@data-channel='true']"
        chunks = re.findall("([A-Za-z\.]+)([0-9]+)(.+)", url)
        if len(chunks):
            pre, num, post = chunks[0]
            num = int(num)
            extra = 0
            while True:
                if extra > 3:
                    break
                dom2 = "https://" + pre + str(num + extra) + post
                print "trying %s" % dom2
                try:
                    page = self.download(dom2, text=False)
                    tree = htmlement.fromstring(page.content)
                    channels = tree.findall(xpath)
                except Exception:
                    extra += 1
                    continue
                if not len(channels):
                    extra += 1
                else:
                    url = page.url
                    if url.endswith("/"):
                        url = url[:-1]
                    cfg.cdnlive = url
                    print "url is %s" % cfg.cdnlive
                    return tree, channels
        else:
            page = self.download(url)
            tree = htmlement.fromstring(page)
            return tree, tree.findall(xpath)

    def getmeta(self, channel):
        datastream = channel.get("data-stream")
        title = channel.get("data-name")
        img = channel.find(".//img")
        if img is not None:
            img = img.get("src")
        else:
            img = "DefaultFolder.png"
        return datastream, title, img

    def iteratechannels(self):
        cpage, channels = self.getitems(cfg.cdnlive)
        for channel in channels:
            datastream, title, img = self.getmeta(channel)
            url = cfg.cdnlive + "/canli-izle/" + datastream
            yield self.makechannel(url, chan,
                                   url=url,
                                   title=title,
                                   icon=img,
                                   cpage=cpage,
                                   datastream=datastream,
                                   categories=["cdnlive"])

    def getchannel(self, url):
        cpage, channels = self.getitems(url)
        for channel in channels:
            cls = channel.get("class")
            if cls and "active" in cls:
                datastream, title, img = self.getmeta(channel)
                return self.makechannel(url, chan,
                                        url=url,
                                        title=title,
                                        cpage=cpage,
                                        icon=img,
                                        datastream=datastream,
                                        categories=["cdnlive"])
