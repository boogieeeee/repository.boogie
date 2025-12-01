'''
Created on Oct 7, 2025

@author: boogie
'''
from tinyxbmc import stubmod
from streams import StreamsBase
from tinyxbmc import net
from tinyxbmc import mediaurl
import ghub

from urllib import parse
import re
import binascii
import json
import base64


ghub.load("ricmoo", "pyaes", None)
import pyaes

IV = b'1234567890oiuytr'
KEY = b'kiemtienmua911ca'


class CloudNestra(StreamsBase):
    regex = r"cloudnestra\."

    def deobfus(self, txt):
        if "https://" in txt:
            return txt
        txt = txt[2:]
        last = None
        for check in ["==", "="]:
            if txt.endswith(check):
                txt = txt[:-len(check)]
                last = check
                break
        parts = []
        for part in re.split(r"/@#@/.+?==", txt):
            subpart = part.split("=")[-1]
            if subpart:
                parts.append(subpart)
        if last:
            parts.append(last)
        based = "".join(parts)
        return base64.b64decode(based).decode()

    def resolve(self, url, headers):
        up = parse.urlparse(url)
        origin = f"{up.scheme}://{up.netloc}"
        referer = origin + "/"
        src = net.http(url, referer=referer)
        urls = re.findall(r"file\s*?\:\s*?(?:\"|\')(.+?)(?:\"|\')", src)
        try:
            url = self.deobfus(urls[-1])
        except Exception:
            return
        yield mediaurl.HlsUrl(url, headers={"origin": origin,
                                            "referer": referer})


class PrimeVid(StreamsBase):
    regex = r"primevid\."

    def decrypt(self, cipher):
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(KEY, IV))
        ddata = decrypter.feed(binascii.unhexlify(cipher[:-1]))
        ddata += decrypter.feed()
        return ddata.decode('utf-8')

    def resolve(self, link, headers):
        vidid = link.split("#")[-1]
        up = parse.urlparse(link)
        host = f"{up.scheme}://{up.netloc}"
        referer = host + "/"
        player = net.http(f"{host}/api/v1/video",
                          params={"id": vidid, "r": up.netloc},
                          referer=referer)
        ddata = json.loads(self.decrypt(player))
        hls = ddata.get("hls", ddata.get("cf"))
        hls = net.absurl(hls, referer)
        yield mediaurl.HlsUrl(hls, headers={"referer": referer, "origin": host}, adaptive=False)
