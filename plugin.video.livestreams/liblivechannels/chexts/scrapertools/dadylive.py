from tinyxbmc import net, tools
from six.moves.urllib import parse
import htmlement
import re


dom = "https://daddylive.me"
mrgx = "source\s*?\:\s*?(?:\'|\")(.+?)(?:\'|\")"
ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"


def getchanurl(chname):
    for a in htmlement.fromstring(net.http("%s/24-hours-channels.php" % dom, cache=60 * 24)).iterfind(".//div[@class='grid-item']/a"):
        if tools.elementsrc(a).lower().strip().replace(" ", "") == chname:
            return net.absurl(a.get("href"), dom)


def itermedias(dadyid=None, dadyname=None):
    if not dadyid:
        u = getchanurl(dadyname)
    else:
        u = "%s/embed/stream-%s.php" % (dom, dadyid)
    iframeu = htmlement.fromstring(net.http(u)).find(".//iframe").get("src")
    iframe = net.http(iframeu, referer=u)
    iframeu2 = re.search("iframe\s*?src=(?:\'|\")(.+?)(?:\'|\")", iframe).group(1)
    iframe = net.http(iframeu2, referer=iframeu)
    src = re.findall(mrgx, iframe)
    ref = parse.urlparse(iframeu2)
    ref = "%s://%s/" % (ref.scheme, ref.netloc)
    yield net.hlsurl(src[0], headers={"Referer": ref, "User-Agent": ua}, adaptive=False)
