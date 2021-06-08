'''
Created on Jun 8, 2021

@author: boogie
'''
from tinyxbmc import net
from tinyxbmc import const
import re

sdom = "https://www.wmsxx.com/"
surl = sdom + "poscitech.php?live=%s&vw=100vw&vh=100vh"
referer = "https://poscitech.club/"
rgx = "source\s*?\:\s*?(?:\"|\")(.+?)(?:\"|\")"


def get(streamid):
    url = surl % streamid
    page = net.http(url, referer=referer)
    m3 = re.search(rgx, page).group(1)
    return net.tokodiurl(m3, headers={"Referer": sdom, "User-Agent": const.USERAGENT})
