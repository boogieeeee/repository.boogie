from liblivechannels import scrapers, scraper
from liblivechannels import config

from tinyxbmc import net
from tinyxbmc import tools

import re
import htmlement

cfg = config.config()


class chan(scraper):
    subchannel = True
    cpage = None

    def get(self):
        if not self.cpage:
            self.cpage = self.download(self.url, referer=cfg.cdnlive)
        pframe = re.search("playerFrame\:\s?(?:\"|')(.+?)(?:\"|')", self.cpage)
        src = self.download(pframe.group(1), referer=self.url)
        b64 = re.search("eval\(atob\((?:\"|')(.+?)(?:\"|')\)", src)
        source = re.search("src\:\s?(?:\"|')(.+?)(?:\"|')", b64.group(1).decode("base64"))
        yield net.tokodiurl(source.group(1), None, {"Referer": pframe.group(1)})


class cdnlive(scrapers):
    def getitems(self):
        # find the domain name automatically, this domain keeps changing
        xpath = ".//div[@id='channel-list']/div/div"
        domain = cfg.cdnlive
        chunks = re.findall("([A-Za-z\.]+)([0-9]+)(.+)", domain)
        if len(chunks):
            pre, num, post = chunks[0]
            num = int(num)
            while True:
                dom2 = "https://" + pre + str(num) + post
                if num >= 100:
                    break
                print "trying %s" % dom2
                try:
                    page = self.download(dom2)
                    tree = htmlement.fromstring(page)
                    channels = tree.findall(xpath)
                except Exception:
                    num += 1
                    continue
                if not len(channels):
                    num += 1
                else:
                    cfg.cdnlive = dom2
                    return channels
        else:
            page = self.download("https://" + domain)
            tree = htmlement.fromstring(page)
            return tree.findall(xpath)

    def iteratechannels(self):
        for channel in self.getitems():
            if "live" not in channel.get("class"):
                # ignore events get only channels
                continue
            a = channel.find(".//a")
            url = a.get("href")
            title = a.get("title")
            if title is not None and url is not None:
                yield self.makechannel(url, chan, title=title, url=url, categories=["cdnlive"])

    def getchannel(self, url):
        cpage = self.download(url, referer=cfg.cdnlive)
        tree = htmlement.fromstring(cpage)
        title = tools.elementsrc(tree.find(".//a[@class='text-white']")).strip()
        return self.makechannel(url, chan, url=url, title=title, cpage=cpage, categories=["cdnlive"])
