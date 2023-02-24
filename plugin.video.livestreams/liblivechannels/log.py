'''
Created on 28 Ara 2018

@author: boogie
'''
import logging


class Logger(object):
    def __init__(self, level=20, Log=None):
        fmt = '%(asctime)s: %(levelname)s: %(module)s.%(funcName)s: %(message)s'
        logging.basicConfig(format=fmt)
        self.Logger = logging.getLogger()
        self.setlevel(level)

    def setlevel(self, level=0):
        self.Logger.setLevel(level)

    def debug(self, text):
        self.Logger.debug(text)

    def info(self, text):
        self.Logger.info(text)

    def error(self, text):
        self.Logger.error(text)

    def critical(self, text):
        self.Logger.critical(text)

    def warning(self, text):
        self.Logger.warning(text)


class LoggerWriter:
    def __init__(self, callback):
        self.callback = callback

    def write(self, message):
        for msg in message.split("\n"):
            self.callback(msg)
