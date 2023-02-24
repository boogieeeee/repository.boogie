'''
Created on Oct 6, 2022

@author: boogie
'''
from tinyxbmc import addon
from tinyxbmc import gui

from aceengine import backend
from aceengine import const


class AceService(addon.blockingloop):
    def oninit(self):
        self.wait = 1
        self.settings = addon.kodisetting(const.ADDONID)
        self.backend = backend.getbackend(self.settings)
        if self.backend:
            self.startengine()

    def startengine(self):
        self.backend.start()
        if self.backend.isrunning:
            if self.backend.wasrunning:
                gui.notify("Acestream", "Connected existing Acestream Engine")
            else:
                gui.notify("Acestream", "Started new Acestream Engine")
        else:
            gui.notify("Acestream", "Can not initiate Acestream Engine")

    def onclose(self):
        if self.backend and self.backend.isrunning and not self.backend.wasrunning:
            self.backend.stop()
            gui.notify("Acestream", "Stopped Acestream Engine")


if __name__ == "__main__":
    AceService()
