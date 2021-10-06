'''
Created on Aug 5, 2021

@author: boogie
'''
import time
from datetime import datetime
import xbmc
import xbmcgui

from tinyxbmc import tools

LOCALTZ = tools.tz_local()


# credits to: https://github.com/primaeval/plugin.video.iptv.recorder
dtformat = xbmc.getRegion('time').replace('%H%H', '%H').replace('%I%I', '%I')
dtformat = dtformat.replace(":%S", "")
dtformat = "{}, {}".format(xbmc.getRegion('datelong'), dtformat)


def extractts(dateLabel, timeLabel):
    # credits to: https://github.com/primaeval/plugin.video.iptv.recorder
    date = xbmc.getInfoLabel(dateLabel)
    timeString = xbmc.getInfoLabel(timeLabel)
    fullDate = "{}, {}".format(date, timeString)

    # https://bugs.python.org/issue27400
    try:
        parsedDate = datetime.strptime(fullDate, dtformat)
    except TypeError:
        parsedDate = datetime(*(time.strptime(fullDate, dtformat)[0:6]))
    parsedDate = parsedDate.replace(tzinfo=LOCALTZ)
    return parsedDate.timestamp()


channel = xbmc.getInfoLabel("ListItem.ChannelName")
title = xbmc.getInfoLabel("ListItem.Label")
start = extractts("ListItem.StartDate", "ListItem.StartTime")
stop = extractts("ListItem.EndDate", "ListItem.EndTime")
