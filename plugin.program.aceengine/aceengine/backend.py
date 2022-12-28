'''
Created on Oct 6, 2022

@author: boogie
'''
from tinyxbmc import abi
from tinyxbmc import net
from aceengine import const

import subprocess
import time
import signal
import os


def getbackend(settings):
    os = abi.detect_os()
    if os == "linux":
        return LinuxBackend(settings)
    elif os == "windows":
        return WindowsBackend(settings)
    elif os == "android":
        return AndroidBackend(settings)


class LinuxBackend:
    def __init__(self, settings):
        self.version = None
        self.settings = settings
        self.wasrunning = False
        self._isrunning = False
        self.process = None
        self.binary = const.BINARY
        self.checkversion()

    @property
    def isrunning(self):
        return self._isrunning

    @isrunning.setter
    def isrunning(self, value):
        self._isrunning = value
        if value:
            self.settings.set(const.SETTING_ACTIVEADDRESS, self.apiurl)
        self.settings.set(const.SETTING_ISRUNNING, value)

    @property
    def apiurl(self):
        if self.settings.getbool(const.SETTING_ISREMOTE):
            addr = self.settings.getstr(const.SETTING_ADDRESS)
        else:
            addr = "127.0.0.1"
        return "http://%s:%d" % (addr, self.settings.getint(const.SETTING_PORT))

    def checkversion(self):
        try:
            resp = net.http("%s/webui/api/service?method=get_version&format=json" % self.apiurl,
                            json=True,
                            cache=None)
        except Exception:
            resp = {""}
        if "result" in resp and "version" in resp["result"]:
            self.version = resp["result"]
        return self.version

    def spawn(self):
        cmd = [self.binary, "--client-console",
               "--max-connections", str(self.settings.getint(const.SETTING_MAXCONS)),
               "--max-peers", str(self.settings.getint(const.SETTING_MAXPEERS)),
               "--max-upload-speed", str(self.settings.getint(const.SETTING_MAXUP)),
               "--max-download-speed", str(self.settings.getint(const.SETTING_MAXDOWN)),
               ]
        cwd = self.settings.getstr(const.SETTING_CWD) if self.settings.getbool(const.SETTING_USECWD) else None
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=cwd)
        except Exception:
            return False
        retval = False
        for _lineno in range(const.MAXLINES):
            line = self.process.stdout.readline()
            if "port=%d" % self.settings.getint(const.SETTING_PORT) in line.decode():
                retval = True
                break
        return retval

    def start(self):
        isrunning = self.checkversion()
        if isrunning:
            self.wasrunning = True
            self.isrunning = True
        else:
            for _retry in range(const.RETRY):
                if self.spawn():
                    isrunning = self.checkversion()
                    if isrunning:
                        self.isrunning = True
                        break

    def stop(self):
        if self.process and not self.wasrunning and self.checkversion():
            # on linux the main app is running +1 pid
            os.kill(self.process.pid + 1, signal.SIGINT)
            for _second in range(const.CLOSETIMEOUT):
                if self.process.poll() is None:
                    time.sleep(1)
                else:
                    break
            if self.process.poll() is None:
                os.kill(self.process.pid + 1, signal.SIGKILL)
        self.isrunning = False
        self.wasrunning = False
        self.version = None


class WindowsBackend(LinuxBackend):
    def __init__(self, settings):
        super(WindowsBackend, self).__init__(settings)
        self.binary = self.binary + ".exe"


class AndroidBackend(LinuxBackend):
    def spawn(self):
        return False
