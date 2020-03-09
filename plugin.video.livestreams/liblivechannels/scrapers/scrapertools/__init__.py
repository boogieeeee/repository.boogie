# -*- coding: utf-8 -*-
import datetime
from liblivechannels import programme
from tinyxbmc import tools


class dateparser(object):
    def __init__(self, timezone=None, localyear=None, localmonth=None, localday=None, shiftdate=True):
        self.timezone = timezone
        self.tz_loc = tools.tz_utc()
        if self.timezone:
            self.tz_loc.settimezone(self.timezone)
        now = datetime.datetime.now()
        if not localday:
            localday = now.day
        if not localmonth:
            localmonth = now.month
        if not localyear:
            localyear = now.year
        if shiftdate:
            self.loc_now = datetime.datetime(localyear, localmonth, localday,
                                             now.hour, now.minute, now.second, tzinfo=tools.tz_local()).astimezone(self.tz_loc)
        else:
            self.loc_now = datetime.datetime(localyear, localmonth, localday,
                                             now.hour, now.minute, now.second, tzinfo=self.tz_loc)

    def datefromhour(self, hour, minute=0, second=0, daydelta=0):
        offset = self.loc_now + datetime.timedelta(days=daydelta)
        return datetime.datetime(offset.year, offset.month, offset.day,
                                 int(hour), int(minute), int(second),
                                 tzinfo=self.tz_loc)


tr_months = {u"ocak": 1, u"oca": 1,
             u"şubat": 2, u"subat": 2, u"şub": 2, u"sub": 2,
             u"mart": 3, u"mar": 3,
             u"nisan": 4, u"nis": 4,
             u"mayıs": 5, u"mayis": 5, u"may": 5,
             u"haziran": 6, u"haz": 6,
             u"temmuz": 7, u"tem": 7,
             u"ağustos": 8, u"agustos": 8, u"agu": 8, u"ağu": 8,
             u"eylül": 9, u"eylul": 9, u"eyl": 9,
             u"ekim": 10, u"eki": 10,
             u"kasım": 11, u"kasim": 11, u"kas": 11,
             u"aralık": 12, u"aralik": 12, u"ara": 12
             }


class makeprograms(object):
    def __init__(self, enddate=None):
        self.enddate = enddate
        self.date = None
        self.title = None
        self.args = None
        self.kwargs = None

    def add(self, title, date, *args, **kwargs):
        p = None
        if self.date is not None:
            p = programme(self.title, self.date, date, *self.args, **self.kwargs)
        self.date = date
        self.title = title
        self.args = args
        self.kwargs = kwargs
        return p

    def flush(self):
        if self.date and self.enddate:
            return programme(self.title, self.date, self.enddate, *self.args, **self.kwargs)
        else:
            raise StopIteration
