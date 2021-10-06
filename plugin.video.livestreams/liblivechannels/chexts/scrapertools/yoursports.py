'''
Created on Jul 31, 2021

@author: boogie
'''
from tinyxbmc import net
import htmlement
import re
import base64


domain = "http://yoursports.stream"


class yoursports():
    ysid = "espn2"

    def get(self):
        u = "%s/ing/%s" % (domain, self.ysid)
        p = net.http(u, referer=domain)
        iframeu = htmlement.fromstring(p).find(".//iframe").get("src")
        iframep = net.http(iframeu, referer=u)
        m3path = re.search("atob\((?:\"|\')(.+?)(?:\"|\')\)", iframep).group(1)
        for suffix in ["", "=", "=="]:
            try:
                yield net.hlsurl(net.absurl(base64.b64decode(m3path + suffix).decode(), iframeu), headers={"Referer": iframeu})
                break
            except Exception:
                pass
