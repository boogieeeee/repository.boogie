'''
Created on Feb 22, 2020

@author: boogie
'''
import os
from tinyxbmc import addon

hay_chan = "channels"
hay_playlist = "playlists"
addon_id = "plugin.video.livestreams"
query_timeout = 2
playlist_timeout = 10
dpath = os.path.join(os.path.dirname(__file__), "chexts")
mpath = os.path.join(os.path.dirname(__file__), "media")
epath = os.path.join(addon.get_addondir(addon_id), "epg.xml")
INPUTSTREAMADAPTIVE = "adaptive"
INPUTSTREAMFFMPEG = "ffmpegdirect"
