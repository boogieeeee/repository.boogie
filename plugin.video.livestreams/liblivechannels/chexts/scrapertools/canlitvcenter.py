'''
Created on Aug 2, 2021

@author: boogie
'''
from tinyxbmc import net
import htmlement
import re
import base64


dom = "canlitv.center"
domain = "https://" + dom

rgxkey = "verianahtar[\s\t]*?\=[\s\t]*?(?:\"|\')(.+?)(?:\"|\')"
rgxlink = "yayin[a-zA-Z0-9]+[\s\t]*?\=[\s\t]*?(?:\"|\')(.*?)(?:\"|\')"


def itermedias(ctvcid, ctvcids=None):
    if not ctvcids:
        ctvcids = [ctvcid]
    for ctvcid in ctvcids:
        links = {}
        u = domain + "/" + ctvcid
        iframe1 = htmlement.fromstring(net.http(u, referer=domain)).find(".//iframe").get("src")
        iframe2 = htmlement.fromstring(net.http(iframe1, referer=u)).find(".//iframe").get("src")
        src = net.http(iframe2, referer=iframe1)
        media = re.search("file[\s\t]*?\:[\s\t]*?atob\((?:\"|\')(.+?)(?:\"|\')\)", src)
        if media:
            link = base64.b64decode(media.group(1)).decode()
            links[link] = net.hlsurl(link, headers={"referer": domain})
        else:
            for script in htmlement.fromstring(src).iterfind(".//script"):
                ssrc = script.get("src")
                if ssrc and ("yayin" in ssrc or "/play.php" in ssrc):
                    scriptsrc = net.http(script.get("src"), referer=domain)
                    key = re.search(rgxkey, scriptsrc)
                    if key:
                        for link in re.findall(rgxlink, scriptsrc):
                            if "anahtar" in link:
                                link = net.absurl(link, script.get("src"))
                                links[link] = net.hlsurl(link + key.group(1), headers={"referer": domain})
        for link in links.values():
            yield link
