# -*- coding: utf-8 -*-
'''
@author: boogie
'''

from tinyxbmc import addon
from tinyxbmc import hay
from tinyxbmc import tools
import common
import urlparse


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
    def selcuk(self):
        up = urlparse.urlparse(self.setting.getstr("selcuk"))
        if up.netloc == "":
            domain = up.path
        else:
            domain = up.netloc
        domain = domain.replace("/", "")
        return "http://" + domain

    @selcuk.setter
    def selcuk(self, value):
        self.setting.set("selcuk", value)

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
    def port(self):
        return self.setting.getint("port")

    @property
    def resolve_mode(self):
        modes = {"First highest quality variant in first alive stream": 0,
                 "First alive stream with all variants": 1,
                 "All streams with all variants redundantly": 2
                 }
        return modes[self.setting.getstr("pvr_resolve_mode")]

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
        for icon, title, index, cats in self.channels:
            yield icon, title, index, cats

    def itercats(self):
        cats = []
        for _icon, _title, _index, chancats in self.iterchannels():
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
