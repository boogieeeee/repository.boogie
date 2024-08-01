try:
    import unittest
    import test

    class testcalitvme(unittest.TestCase):
        def test_daddy_link(self):
            test.testlink(self, itermedias("TRT 1"), 1, "TRT Spor Yildiz", 0)

except ImportError:
    pass

from tinyxbmc import net
from tinyxbmc import tools
from tinyxbmc import mediaurl
import htmlement
import re

domain = "https://www.canlitv.me"

def deobfuslink(page):
    fileaddrs = re.findall('changeVideo\((?:\'|\")(.+?)(?:\'|\")\)', page)
    if not fileaddrs:
        fileaddrs = re.findall('file\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")', page)
    for fileaddr in fileaddrs:
        shift = int(re.search("(^[0-9]+)", fileaddr).group(1))
        prev_c = None
        start_index = 0
        for index, c in enumerate(fileaddr):
            if c == prev_c:
                # https:/(/)
                if start_index and index == start_index + 7:
                    break
                # ht(t)ps://
                start_index = index - 2
            prev_c = c
        fileaddr = fileaddr[start_index:]
        arrays = []
        for arr in re.findall("\=\s*?(\[.+?\])", page):
            try:
                isvalid = True
                arr = eval(arr)
                for item in arr:
                    if len(item) != 1:
                        isvalid = False
                        break
                if not isvalid:
                    continue
                arrays.append(arr)
            except:
                continue
        translation = dict(zip(arrays[0][shift:] + arrays[0][:shift], arrays[3]))
        yield fileaddr.translate(fileaddr.maketrans(translation))

def searchkw(kw):
    spage = htmlement.fromstring(net.http(domain, referer=domain))
    form = spage.find(".//form")
    sec = form.find(".//input[@name='security']").get("value")
    lpage = htmlement.fromstring(net.http(form.get("action"), params={"s": kw, "security": sec}, referer=domain))
    for channel in lpage.iterfind(".//li[@class='canlitvlist']/.//a"):
        chname = channel.get("title").lower().replace(" ", "")
        if chname == kw.lower().replace(" ", ""):
            chpage = htmlement.fromstring(net.http(channel.get("href"), referer=domain))
            for alt in chpage.iterfind(".//ul[@class='alternatif']/.//a"):
                yield alt.get("href")


def itermedias(keyword):
    for u in searchkw(keyword):
        upage = htmlement.fromstring(net.http(u, referer=domain))
        geo = upage.find(".//iframe").get("src")
        gpage = net.http(geo, referer=u)
        yayin = re.findall('src="(.+?ulke.+?)"', gpage)[-1]
        yayin = yayin.replace("'+ulke+'", "DE")
        ypage = net.http(yayin, referer=geo)
        for ylink in tools.safeiter(deobfuslink(ypage)):
            yield mediaurl.hlsurl(ylink, headers={"referer": domain + "/"}, adaptive=True, ffmpegdirect=False)
