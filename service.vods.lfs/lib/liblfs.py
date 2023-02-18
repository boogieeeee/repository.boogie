'''
Created on Jun 4, 2022

@author: boogie
'''
import htmlement
import re
import json
from tinyxbmc import net, mediaurl

dom = "https://soccerstreamslive.co"
streamdom = "https://cloudstreams.org"

def get(streamid):
    u = "%s/hdl%s.html" % (dom, streamid)
    iframeu = htmlement.fromstring(net.http(u)).find(".//iframe")
    if iframeu is not None:
        iframe = net.http(iframeu.get("src"), referer=u)
        fid = re.search("fid\s*?\=\*?(?:\'|\")(.+?)(?:\'|\")", iframe)
        if fid is not None:
            cloud = net.http("%s/cloud.php?player=desktop&live=%s" % (streamdom, fid.group(1)), cache=None)
            url = re.search('return\((\[.+?\])', cloud).group(1)
            url = "".join(json.loads(url))
            return mediaurl.hlsurl(url, headers={"Referer": streamdom}, adaptive=False)