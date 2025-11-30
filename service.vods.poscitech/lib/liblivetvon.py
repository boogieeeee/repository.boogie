'''
Created on Jun 6, 2022

@author: boogie
'''
import htmlement
import re
import json
import base64
import traceback
from datetime import datetime
from tinyxbmc.addon import kodisetting
from tinyxbmc import net
from tinyxbmc import mediaurl
from tinyxbmc import tools
from six.moves.urllib import parse


setting = kodisetting("service.vods.poscitech")
domain = "https://" + setting.getstr("domain")
dtrgx = r"([0-9]{1,2})[\sa-zA-Z]*?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-zA-Z\s]*?([0-9]{4})"

monthtoint = {"jan": 1,
              "feb": 2,
              "mar": 3,
              "apr": 4,
              "may": 5,
              "jun": 6,
              "jul": 7,
              "aug": 8,
              "oct": 9,
              "nov": 10,
              "sep": 11,
              "dec": 12}


def get_forcedplay(iframe, iframeu, referer):
    jsvars = {}
    iframeu_p = parse.urlparse(iframeu)
    orig = iframeu_p.scheme + "://" + iframeu_p.netloc
    headers = {"Origin": orig,
               "Referer": orig + "/",
               }
    for varname in re.findall(r"JSON\.parse\(atob\((.+?)\)\)", iframe):
        try:
            bstr = re.search(varname + r"\s*?\=\s*?(?:\"|\')(.+?)(?:\"|\')", iframe).group(1)
            jstr = base64.b64decode(bstr).decode()
            for k, v in json.loads(jstr).items():
                jsvars[k] = base64.b64decode(v).decode()
            channelid = re.search(r"CHANNEL_KEY\s*?\=\s*?(?:\"|\')(.+?)(?:\"|\')", iframe).group(1)
            params = {"channel_id": channelid,
                      "ts": jsvars["b_ts"],
                      "rnd": jsvars["b_rnd"],
                      "sig": jsvars["b_sig"]}
            try:
                auth = re.search(r"Array\(\[([0-9,\s]+?)\]\).+\^([0-9]+)", iframe)
                auth_chars = [int(c.strip()) for c in auth.group(1).split(",")]
                auth_page = "".join([chr(c ^ int(auth.group(2))) for c in auth_chars])
            except:
                auth_page = "auth.php"
            authurl = f"{jsvars['b_host']}{auth_page}" 
            _auth = net.http(authurl, params=params, headers=headers)
            break
        except Exception:
            pass
    lookupurl = re.search(r"(?:\"|\')(.+?server_lookup\.php.*?)\?", iframe).group(1)
    params = {"channel_id": channelid}
    lookup = net.http(net.absurl(lookupurl, iframeu), params=params, json=True)
    server_key = lookup["server_key"]
    pre = server_key.split("/")[0]
    post = server_key
    murl = f"https://{pre}new.newkso.ru/{post}/{channelid}/mono.m3u8"
    return mediaurl.HlsUrl(murl, headers=headers, adaptive=True, ffmpegdirect=False, lheaders=headers)


def getzippy(iframe, iframeu, referer):
    new_iframeu = re.search(r"<iframe\s*?src=(?:\"|\')(.+?)(?:\"|\')", iframe).group(1)
    if new_iframeu.endswith("="):
        new_iframeu += domain
    new_iframe = net.http(new_iframeu, referer=iframeu)
    new_xiframe = htmlement.fromstring(new_iframe)
    url = new_xiframe.find(".//input[@id='crf__']").get("value")
    url = base64.b64decode(url).decode()
    channel = json.loads(re.search(r"CHANNEL\s*?=\s*?({.+?})", new_iframe).group(1))
    origin = "https://" + channel["origin"]
    headers = {"Referer": origin + "/",
               "Origin": origin,
               "Xauth": channel["auth"],
               }
    return mediaurl.HlsUrl(url, headers=headers, adaptive=True, ffmpegdirect=False, lheaders=headers)


def geturls(streamid, path="/stream/stream-%s.php"):
    u = ("%s" + path) % (domain, streamid)
    xpage = htmlement.fromstring(net.http(u, referer=domain + "/"))
    iframeus = [net.absurl(a.get("href"), u) for a in xpage.findall(".//center/center/a")]
    if not iframeus:
        iframeus = [u]
    iframeus = set(iframeus)
    for iframeu in iframeus:
        iframe = net.http(iframeu, referer=u)
        xiframe = htmlement.fromstring(iframe)
        for subiframe in xiframe.iterfind(".//iframe"):
            if subiframe.get("src") and subiframe.get("src").startswith("https://"):
                iframeu2 = subiframe.get("src")
                try:
                    iframe2 = net.http(iframeu2, referer=u)
                except Exception:
                    continue
                for cb in [get_forcedplay, getzippy]:
                    try:
                        media = cb(iframe2, iframeu2, u)
                        if media:
                            yield media
                            break
                    except Exception:
                        print(traceback.format_exc())
                break


def getschdate(page):
    today = datetime.now()
    for dtmatch in re.finditer(dtrgx, page, re.IGNORECASE):
        day = int(dtmatch.group(1))
        month = monthtoint[dtmatch.group(2).lower().strip()]
        year = int(dtmatch.group(3))
        tz = tools.tz_utc()
        tz.settimezone(0)
        dtob = datetime(day=day, month=month, year=year, tzinfo=tz)
        return dtob
    return today


def getevents():
    allevents = []
    loctz = tools.tz_local()
    schedules = {"schedule-extra-generated.php": "/extra/stream-%s.php",
                 "schedule-generated.php": "/stream/stream-%s.php",
                 "extra2-schedule-2.php": "/stream/bet.php?id=%s"}
    for schedule, path in schedules.items():
        js = net.http(f"{domain}/schedule/{schedule}", referer=domain, json=True)
        for dt, members in js.items():
            sch_date = getschdate(dt)
            for category, events in members.items():
                category = re.sub(r"<.*?>", "", category).strip()
                if category == "All matches":
                    pass
                for event in events:
                    title = event["event"]
                    evdtmatch = re.search(r"([0-9]{1,2})\:([0-9]{1,2})(.*)", event["time"])
                    hour = int(evdtmatch.group(1))
                    minute = int(evdtmatch.group(2))
                    evdate = datetime(hour=hour, minute=minute,
                                      year=sch_date.year, month=sch_date.month, day=sch_date.day,
                                      tzinfo=sch_date.tzinfo)
                    channels = []
                    if isinstance(event["channels"], dict):
                        evchannels = list(event["channels"].values())
                    else:
                        evchannels = event["channels"]
                    for channel in evchannels:
                        channel["channel_id"].isdigit()
                        if(channel["channel_id"]).isdigit():
                            name = f"{channel['channel_name']}({channel['channel_id']})"
                            channels.append([name, int(channel["channel_id"]), path])
                    allevents.append([evdate.astimezone(loctz), category, title, channels])
    allevents.sort()
    return allevents


def getchmeta(numbyname=False, nameidbynum=False):
    response = net.http(domain + "/24-7-channels.php", cache=60 * 24, text=False)
    up = parse.urlparse(response.url)
    if not up.hostname == setting.getstr("domain"):
        setting.set("domain", up.hostname)
    chnames = {}
    for a in htmlement.fromstring(response.content.decode()).iterfind(".//div[@class='grid-item']/a"):
        href = a.get("href")
        if href is not None:
            chnum = re.search(r"stream\-([0-9]+)\.", href)
            if chnum:
                chnum = int(chnum.group(1))
                if numbyname:
                    chnames[chnum] = tools.elementsrc(a)
                elif nameidbynum:
                    chnames[tools.elementsrc(a).lower().replace(" ", "").strip()] = chnum
    return chnames
