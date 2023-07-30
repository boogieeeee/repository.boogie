# -*- coding: utf-8 -*-
'''
@author: boogie
'''

from tinyxbmc import addon
from tinyxbmc import hay
from tinyxbmc import tools
from tinyxbmc import gui

from liblivechannels import common
from datetime import datetime
from tinyxbmc.tools import tz_local

loc_tz = tz_local()

class config(object):
    def __init__(self):
        self.setting = addon.kodisetting(common.addon_id)
        self.hay = hay.stack(common.hay_chan, aid=common.addon_id)
        self.phay = hay.stack(common.hay_playlist, aid=common.addon_id)

    @property
    def update_pvr(self):
        data = self.hay.find("update_pvr").data
        if data == {}:
            return False
        else:
            return data

    @update_pvr.setter
    def update_pvr(self, value):
        self.hay.throw("update_pvr", bool(value))
        self.hay.snapshot()

    @property
    def update_running(self):
        data = self.hay.find("update_running").data
        if data == {}:
            return False
        else:
            return data

    @update_running.setter
    def update_running(self, value):
        self.hay.throw("update_running", bool(value))
        self.hay.snapshot()

    @property
    def lastupdate(self):
        data = self.hay.find("last_update").data
        if data == {}:
            return 1
        else:
            return data

    @lastupdate.setter
    def lastupdate(self, value):
        self.hay.throw("last_update", float(value))
        self.hay.snapshot()

    @property
    def validate(self):
        return self.setting.getbool("validate")

    @property
    def internetaddress(self):
        url = self.setting.getstr("internetaddress")
        if "://" in url:
            url = url.split("://")[1]
        return url

    @validate.setter
    def validate(self, value):
        self.setting.set("validate", value)

    @property
    def channels(self):
        data = self.hay.find("channels").data
        if data == {}:
            data = []
        return data

    @channels.setter
    def channels(self, value):
        self.hay.throw("channels", list(value))
        self.hay.snapshot()

    @property
    def pvr(self):
        return self.setting.getbool("pvr")

    @property
    def updatetime(self):
        hourmin = self.setting.getstr("updatetime").split(":")
        td = datetime.today()
        return datetime(td.year, td.month, td.day, int(hourmin[0]), int(hourmin[1]), tzinfo=loc_tz).timestamp()
    
    @property
    def pvrtimer(self):
        return int(self.setting.getstr("pvrtimer"))

    @pvr.setter
    def pvr(self, value):
        return self.setting.set("pvr", value)

    @property
    def pvrrecord(self):
        return self.setting.getbool("record")

    @property
    def pvrlocation(self):
        path = tools.translatePath(self.setting.getstr("pvrlocation"))
        if tools.exists(path):
            return path
        else:
            gui.warn("PVR storage path is not available", "Recording Disabled: %s" % path)
            self.setting.set("record", False)

    @property
    def pvrtemp(self):
        if self.setting.getbool("pvrusetemp"):
            path = tools.translatePath(self.setting.getstr("pvrtemplocation"))
            if not tools.exists(path):
                npath = addon.get_addondir(common.addon_id)
                gui.warn("PVR temp path is not available", "Using path %s instead of %s" % (npath, path))
                path = npath
        else:
            path = addon.get_addondir()
        return path

    @property
    def ffmpegdirect(self):
        if addon.has_addon("inputstream.ffmpegdirect"):
            return self.setting.getbool("ffmpegdirect")
        else:
            return False

    @property
    def port(self):
        return self.setting.getint("port")

    @port.setter
    def port(self, val):
        self.setting.set("port", val)

    @property
    def playlists(self):
        return self.phay.find("playlists").data

    def iterplaylists(self, playlists=None):
        if not playlists:
            playlists = self.playlists
        for playlist in playlists:
            yield playlist.title(), playlists[playlist]

    def iterchannels(self):
        for icon, title, index, cats, pvrinputstream, in self.channels:
            yield icon, title, index, cats, pvrinputstream

    def itercats(self):
        cats = []
        for _icon, _title, _index, chancats, _pvrinputstream in self.iterchannels():
            for cat in chancats:
                if cat not in cats:
                    cats.append(cat)
                    yield cat.title()

    def add_playlist(self, playlist):
        playlist = playlist.title()
        playlists = self.playlists
        if playlist in playlists:
            return False
        for cat in self.itercats():
            if cat == playlist or playlist == "Broken":
                return False
        playlists[playlist] = []
        self.phay.throw("playlists", playlists)
        self.phay.snapshot()
        return True

    def delete_playlist(self, playlist):
        playlist = playlist.title()
        playlists = self.playlists
        if playlist not in playlists:
            return False
        playlists.pop(playlist)
        self.phay.throw("playlists", playlists)
        self.phay.snapshot()
        return True

    def add_to_playlist(self, playlist, index):
        playlist = playlist.title()
        playlists = self.playlists
        if playlist not in playlists:
            return False
        if index in playlists[playlist]:
            return False
        playlists[playlist].append(index)
        self.phay.throw("playlists", playlists)
        self.phay.snapshot()
        return True

    def remove_from_playlist(self, playlist, index):
        playlist = playlist.title()
        playlists = self.playlists
        if playlist in playlists and index in playlists[playlist]:
            playlists[playlist].remove(index)
            self.phay.throw("playlists", playlists)
            self.phay.snapshot()
            return True

    def rename_playlist(self, playlist_old, playlist_new):
        playlist_old = playlist_old.title()
        playlist_new = playlist_new.title()
        for cat in self.itercats():
            if cat.lower() == playlist_new.lower():
                return False
        playlists = self.playlists
        if playlist_new not in playlists:
            playlists[playlist_new] = playlists.pop(playlist_old)
            self.phay.throw("playlists", playlists)
            self.phay.snapshot()
            return True
