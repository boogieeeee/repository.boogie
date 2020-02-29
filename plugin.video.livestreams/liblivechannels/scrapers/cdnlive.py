from liblivechannels import scrapers, scraper
from liblivechannels import config

from tinyxbmc import net

import re
import htmlement

cfg = config.config()


class chan(scraper):
    subchannel = True
    tree = None

    def get(self):
        if not self.tree:
            cpage = self.download(self.url, referer=cfg.cdnlive)
            self.tree = htmlement.fromstring(cpage)
        for iframe in self.tree.findall(".//iframe"):
            src = iframe.get("src")
            if "/channel/watch" in src:
                ipage = self.download(src, referer=self.url)
                b64 = re.search(r'eval\(atob\("(.+?)"\)\)', ipage)
                if b64:
                    code = b64.group(1).decode("base64")
                    for source in re.findall("source:\s*?(?:'|\")(http.+?)(?:'|\")", code):
                        if ".m3u8" in source:
                            yield net.tokodiurl(source, None, {"Referer": src})
                            break
                        break

class cdnlive(scrapers):
    def getitems(self):
        xpath = ".//div[@id='channel-list']/.//a"
        domain = cfg.cdnlive
        chunks = re.findall("([A-Za-z\.]+)([0-9]+)(.+)", domain)
        if len(chunks):
            pre, num, post = chunks[0]
            num = int(num)
            while True:
                dom2 = "https://" + pre + str(num) + post
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
                if num >= 100:
                    break
        else:
            page = self.download("https://" + domain)
            tree = htmlement.fromstring(page)
            return tree.findall(xpath)
    
    def iteratechannels(self):
        for channel in self.getitems():
            live = channel.find('.//span[@class="live"]')
            if live is None:
                continue
            url = channel.get("href")
            title = channel.get("title")
            if title is not None and url is not None:
                yield self.makechannel(url, chan, title=title, url=url, categories=["cdnlive"])
                
    def getchannel(self, url):
        cpage = self.download(url, referer=cfg.cdnlive)
        tree = htmlement.fromstring(cpage)
        title = tree.find(".//h1[@class='match-title']").text.strip()
        return self.makechannel(url, chan, url=url, title=title, tree=tree, categories=["cdnlive"])
