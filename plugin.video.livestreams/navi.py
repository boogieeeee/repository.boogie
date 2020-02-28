'''
Created on Feb 22, 2020

@author: boogie
'''
from addon import Base
from tinyxbmc import container
from tinyxbmc import gui


class Navi(Base):
    def cats(self):
        for cat in self.config.itercats():
            self.item(cat, method="index").dir(cat)
            
    def edit_playlist(self, add=False, rename=False, delete=False, addto=False, removefrom=False, oldname=None, index=None):
        update = False

        if add or rename:
            confirmed, text = gui.keyboard()
            if confirmed:
                if add:
                    result = self.config.add_playlist(text)
                if rename:
                    result = self.config.rename_playlist(oldname, text)
                if not result:
                    gui.warn("ERROR", "Can not edit playlist %s. Either there is already a playlist or a category with the same name" % text)
                else:
                    update = True

        if delete:
            result = self.config.delete_playlist(oldname)
            if not result:
                gui.warn("ERROR", "Can not delete playlist %s. No such playlist" % oldname)
            else:
                update = True

        if addto:
            playlists = self.config.playlists.keys()
            playlist = gui.select("Select Playlist", playlists)
            if playlist >= 0:
                playlist = playlists[playlist]
                result = self.config.add_to_playlist(playlist, index)
                if not result:
                    gui.warn("ERROR", "Can not add channel to playlist %s. Channel is already in the list" % playlist)
                else:
                    update = True
                
        if removefrom:
            print repr(oldname)
            result = self.config.remove_from_playlist(oldname, index)
            if not result:
                gui.warn("ERROR", "Can not remove channel from playlist %s" % oldname)
            else:
                update = True
            
        if update:
            self.config.update_pvr = True
            container.refresh()
            
    def playlists(self):
        self.item("Add Playlist", method="edit_playlist").call(add=True)
        for playlist, _ in self.config.iterplaylists():
            cntx_ren = self.item("Rename Playlist", method="edit_playlist")
            cntx_del = self.item("Delete Playlist", method="edit_playlist")
            item = self.item(playlist, method="index")
            item.context(cntx_ren, False, rename=True, oldname=playlist)
            item.context(cntx_del, False, delete=True, oldname=playlist)
            item.dir(None, playlist)

    def index(self, cat=None, playlistname=None):
        if playlistname:
            playlist = self.config.playlists.get(playlistname)
        else:
            playlist = None
        if self.config.validate or not len(self.config.channels):
            self.do_validate()
            self.config.validate = False
        if not ((cat is None) ^ (playlist is None)):
            self.item("Categories", method="cats").dir()
            self.item("Playlists", method="playlists").dir()
        
        for icon, title, index, cats in self.config.channels:
            cats = [x.title() for x in cats]
            if "Broken" in cats and not (cat == "Broken" or playlist is not None):
                continue
            if cat and cat not in cats:
                continue
            if playlist is not None and index not in playlist:
                continue
            info = {"title": title}
            art = {"icon": icon, "thumb": icon, "poster": icon}
            item = self.item(title, info, art, method="geturls")
            if playlist is not None:
                cntx_plist = self.item("Remove From Playlist", method="edit_playlist")
                cntx_plist_kwargs = {"removefrom": True, "oldname": playlistname, "index": index}
            else:
                cntx_plist = self.item("Add to Playlist", method="edit_playlist")
                cntx_plist_kwargs = {"addto": True, "index": index}
            cntx_validate = self.item("Validate", method="validate_single")
            item.context(cntx_validate, False, index)
            item.context(cntx_plist, False, **cntx_plist_kwargs)
            item.resolve(index)

    def validate_single(self, index):
        channels = self.config.channels
        for channel in channels:
            icon, title, cindex, cats = channel
            if not cindex == index:
                continue
            chan = self.loadchannel(cindex)
            for url in chan.get():
                msg = self.healthcheck(url)
                if msg is None:
                    break
            if msg is None:
                msg = "Channel is UP"
                cats = chan.categories
            else:
                cats = ["Broken"]
            channels.remove(channel)
            channels.append([icon, title, cindex, cats])
            gui.ok("Validation", msg)
            self.config.hay.throw("channels", channels)
            self.config.hay.snapshot()
            container.refresh()
            self.config.update_pvr = True
            break

    def geturls(self, cid):
        chan = self.loadchannel(cid)
        for url in chan.get():
            yield url
Navi()
