# -*- encoding: utf-8 -*-
"""
try:
    import unittest
    from test import ChannelTest

    class testzdf(ChannelTest, unittest.TestCase):
        index = "zdf:zdfmain:"
        minepg = 1

    class testzdfneo(ChannelTest, unittest.TestCase):
        index = "zdf:neo:"
        minepg = 1

    class testzdfinfo(ChannelTest, unittest.TestCase):
        index = "zdf:info:"
        minepg = 1

except ImportError:
    pass


from liblivechannels.chexts.scrapertools.mediathek import multi
from liblivechannels import scraper


class zdfmain(multi, scraper):
    sender = "ZDF Livestream"
    icon = multi.iconpath + "tv-zdf.png"
    title = "ZDF"


class neo(multi, scraper):
    sender = "ZDFneo Livestream"
    icon = multi.iconpath + "tv-zdf-neo.png"
    title = "ZDF-neo"
    epg = "2neo"


class info(multi, scraper):
    sender = "ZDFinfo Livestream"
    icon = multi.iconpath + "tv-zdf-info.png"
    title = "ZDF-info"
    epg = "zinfo"
"""