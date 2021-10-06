'''
Created on Jun 6, 2021

@author: boogie
'''
from tinyxbmc import net
from liblivechannels import unwise

import htmlement
import re


domain = "https://www.canlitvizle.life"

rgx = "}\((?:\"|\')(.*?)(?:\"|\')\s*?\,\s*?(?:\"|\')(.*?)(?:\"|\')\s*?\,\s*?(?:\"|\')(.*?)(?:\"|\')\s*?\,\s*?(?:\"|\')(.*?)(?:\"|\')\)"
rgx2 = "file\s*?\:\s*?(?:\"|\')(.+?)(?:\"|\')"


def itermedias(chlink, chlinks=None):
    if not chlinks:
        chlinks = [chlink]
    for chlink in chlinks:
        url = domain + chlink
        page = htmlement.fromstring(net.http(url, referer=domain))
        iurl = page.find(".//iframe").get("src")
        ipage = net.http(iurl, referer=url)
        wise = unwise.unwise(*re.findall(rgx, ipage)[0])
        wise = unwise.unwise(*re.findall(rgx, wise)[0])
        wise = unwise.unwise(*re.findall(rgx, wise)[1])
        media = re.search(rgx2, wise.replace("\\", "")).group(1)
        yield net.hlsurl(media, headers={"referer": domain + "/"})
