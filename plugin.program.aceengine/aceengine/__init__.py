from . import const
from tinyxbmc import addon
from tinyxbmc import net


settings = addon.kodisetting(const.ADDONID)


def isrunning():
    return settings.getbool(const.SETTING_ISRUNNING)


def apiurl():
    if isrunning():
        return settings.getstr(const.SETTING_ACTIVEADDRESS)


def aceurl(url):
    api = apiurl()
    if api:
        return "%s/ace/getstream?id=%s" % (api, url.lower().replace("acestream://", "").strip())


def _get_engine_url(acestreamurl, key):
    result = net.http(acestreamurl.kodiurl + "&format=json", cache=None, json=True)
    if "response" in result:
        return result["response"].get(key)


def stats(acestreamurl):
    statu = _get_engine_url(acestreamurl, "stat_url")
    if statu:
        return net.http(statu, cache=None, json=True).get("response", {})
    return {}


def stop(acestreamurl):
    cmdu = _get_engine_url(acestreamurl, "command_url")
    if cmdu:
        return net.http(cmdu + "?method=stop", cache=None, json=True).get("response")
