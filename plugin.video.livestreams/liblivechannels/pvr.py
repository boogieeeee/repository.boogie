'''
Created on Aug 3, 2021

@author: boogie
'''
from tinyxbmc import addon
from tinyxbmc import tools

from liblivechannels import config
from liblivechannels import common


import time
import xml.etree.ElementTree as ET

IPTVSIMPLE = "pvr.iptvsimple"

cfg = config.config()


class iptv:
    channels = {}

    @staticmethod
    def getchannels():
        data = {"jsonrpc": "2.0",
                "method": "PVR.GetChannels",
                "params": {"channelgroupid": "alltv"},
                "id": 1}
        return {x["channelid"]: x["label"] for x in tools.jsonrpc(data).get("result", {}).get("channels", [])}

    @staticmethod
    def isenabled():
        iptv = addon.addon_details(IPTVSIMPLE)
        if iptv:
            return iptv.get("enabled")
        else:
            return False

    @staticmethod
    def reload_pvr():
        if iptv.isenabled():
            time.sleep(1)
            addon.toggle_addon(IPTVSIMPLE)
            time.sleep(3)
            addon.toggle_addon(IPTVSIMPLE)

    @staticmethod
    def config_pvr():
        if iptv.isenabled():
            pvr_settings = addon.kodisetting(IPTVSIMPLE)
            if not pvr_settings.getint("m3uPathType") == 1:
                pvr_settings.set("m3uPathType", 1)
            m3uurl = "http://localhost:%s" % cfg.port
            if not pvr_settings.getstr("m3uUrl") == m3uurl:
                pvr_settings.set("m3uUrl", m3uurl)
            if not pvr_settings.getint("epgPathType") == 0:
                pvr_settings.set("epgPathType", 0)
            if not pvr_settings.getstr("epgPath") == common.epath:
                pvr_settings.set("epgPath", common.epath)
            # workaround for binary addons kodi instances
            i_file = pvr_settings._get_file(pvr_settings.aid, "instance-settings-99.xml")
            s_file = pvr_settings._get_file(pvr_settings.aid, "settings.xml")
            tree = ET.parse(s_file)
            root = tree.getroot()
            child = ET.Element("setting", attrib={"id": "kodi_addon_instance_name"})
            child.text = "Livestreams"
            root.append(child)
            child = ET.Element("setting", attrib={"id": "kodi_addon_instance_enabled", "default": "true"})
            child.text = "true"
            root.append(child)
            tree.write(i_file)
