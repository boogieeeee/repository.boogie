'''
Created on Aug 3, 2021

@author: boogie
'''
from tinyxbmc import addon
from tinyxbmc import tools
from tinyxbmc import net
from tinyxbmc import mediaurl
from tinyxbmc import gui

from liblivechannels import config
from liblivechannels import hls
from liblivechannels import common

from thirdparty.m3u8 import parser

import time
import re
import threading
import os
import calendar
import traceback
from datetime import datetime

IPTVSIMPLE = "pvr.iptvsimple"

cfg = config.config()


class iptv:
    activerecords = {}
    channels = {}

    @staticmethod
    def getchannels():
        data = {"jsonrpc": "2.0",
                "method": "PVR.GetChannels",
                "params": {"channelgroupid": "alltv"},
                "id": 1}
        return {x["channelid"]: x["label"] for x in tools.jsonrpc(data).get("result", {}).get("channels", [])}

    @staticmethod
    def deletetimer(timerid):
        data = {"jsonrpc": "2.0",
                "method": "PVR.DeleteTimer",
                "params": {"tiemrid": timerid},
                "id": 1}
        return tools.jsonrpc(data)

    @staticmethod
    def gettimers():
        data = {"jsonrpc": "2.0",
                "method": "PVR.GetTimers",
                "params": {"properties": ["epguid",
                                          "channelid",
                                          "istimerrule",
                                          "isreminder",
                                          "starttime",
                                          "endtime",
                                          "file",
                                          "directory",
                                          "state"]},
                "id": 1}
        return tools.jsonrpc(data).get("result", {}).get("timers", [])

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
            if cfg.pvr:
                iptv.config_pvr()
            time.sleep(1)
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
            iptv.reload_pvr()

    @staticmethod
    def _recorder_thread(timerid, url, fname, startts, endts):
        segmentsdone = []
        hasstarted = False
        stopflag = False
        manifest = re.findall("(http\:\/\/localhost.+)", net.http(url, cache=None))[0]
        fnamenorm = re.sub("[^0-9a-zA-Z]+", "_", fname) + ".ts"
        fullname = os.path.join(cfg.pvrtemp, fnamenorm)
        while True:
            if time.time() > endts or stopflag:
                if fname in iptv.activerecords:
                    iptv.activerecords.pop(fname)
                    tools.copy(fullname, cfg.pvrlocation + "/" + fnamenorm)
                    os.remove(fullname)
                    gui.notify("Recording Finished", "%s is recorded" % fname)
                break
            if not hasstarted:
                gui.notify("Recording Started", "%s is being recorded" % fname)
                hasstarted = True
                iptv.activerecords[fname] = timerid
            lastmanifest = time.time()
            parsed = parser.parse(net.http(manifest, cache=None))
            targetduration = parsed.get("targetduration", 1)
            for segment in parsed.get("segments", []):
                if segment["uri"] not in segmentsdone:  # TO-DO: this can be faster
                    segmentsdone.append(segment["uri"])
                    segmentts = segment.get("current_program_date_time")
                    if segmentts:
                        segmentts = datetime.timestamp(segmentts)  # TO-DO: make sure this is UTC
                        if segmentts < startts:
                            continue
                        elif segmentts > endts:
                            stopflag = True
                            break
                    try:
                        segdata = net.http(segment["uri"], text=False, cache=None).content
                        with open(fullname, "ab") as f:  # TO-do: Windows?
                            f.write(segdata)
                    except Exception:
                        # shit segment, skip it
                        print(traceback.format_exc())
                while True:
                    if (time.time() - lastmanifest) > targetduration:
                        break
                    time.sleep(0.5)

    @staticmethod
    def recorder(timerid, chname, fname, startts, endts):
        for _icon, title, index, _cats, url in cfg.channels:
            if chname == title:
                # TO-DO: improve this, there can be different channels with same name
                if not isinstance(url, mediaurl.mpdurl):
                    url = hls.encodeurl(playlist=index, forceproxy=1)
                    threading.Thread(target=iptv._recorder_thread, args=(timerid, url, fname, startts, endts)).start()
                    break

    @staticmethod
    def shouldrecord():
        for timer in iptv.gettimers():
            if timer["state"] == "disabled":
                continue
            if timer["channelid"] >= 0:
                start = time.mktime(time.strptime(timer["starttime"], "%Y-%m-%d %H:%M:%S"))  # TODO: is timeformat always the same?
                end = calendar.timegm(time.strptime(timer["endtime"], "%Y-%m-%d %H:%M:%S"))
                timerid = timer["timerid"]
                chname = iptv.channels[timer["channelid"]]
                fname = "%s: %s: %s-%s" % (timer["label"], chname, timer["starttime"], timer["endtime"])
                if start <= time.time() < end and fname not in iptv.activerecords and iptv.activerecords.get(fname) != timerid:
                    iptv.recorder(timerid, chname, fname, start, end)
                    iptv.deletetimer(timerid)
