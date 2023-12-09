# -*- encoding: utf-8 -*-
from liblivechannels.chexts.scrapertools import youtube
from liblivechannels.chexts.scrapertools import selcuk
from liblivechannels.chexts.scrapertools import canlitvcenter
from liblivechannels.chexts.scrapertools import dadylive

from liblivechannels.chexts.scrapertools import yayinakisi
from liblivechannels.chexts.scrapertools import vercel
from liblivechannels.chexts.scrapertools import mynetyayin

from liblivechannels import common

from tinyxbmc.tools import safeiter
from tinyxbmc import mediaurl


class multi:
    #acestreams
    acestreams = []
    # kolay tv
    kolay_id = None
    kolay_ids = None

    # selcuk sports
    selcuk_name = None

    # youtube
    youtube_chanid = None
    youtube_sindex = None

    # canlitvcenter
    canlitv_id = None
    canlitv_ids = None

    # dadylive
    dady_id = None
    dady_name = None

    # sports24
    sports24_id = None

    # epg: yayinakisi
    yayin_name = None
    yayin_id = None

    # epg: vercel
    vercel_id = None

    # epg: mynet
    mynet_yayin = None

    def get(self):
        for acestream in self.acestreams:
            self.pvrinputstream = common.INPUTSTREAMFFMPEG
            yield mediaurl.acestreamurl(acestream)
        if self.youtube_chanid:
            for yayin in safeiter(youtube.itermedias(self.youtube_chanid, self.youtube_sindex)):
                yield yayin
        #if self.kolay_id or self.kolay_ids:
        #    for yayin in safeiter(kolaytv.itermedias(self.kolay_id, self.kolay_ids)):
        #        yield yayin
        if self.canlitv_id or self.canlitv_ids:
            for yayin in safeiter(canlitvcenter.itermedias(self.canlitv_id, self.canlitv_ids)):
                yield yayin
        if self.dady_id or self.dady_name:
            for yayin in safeiter(dadylive.itermedias(self.dady_id, self.dady_name)):
                yield yayin
        if self.selcuk_name:
            for yayin in safeiter(selcuk.itermedias(self.selcuk_name)):
                yield yayin
        #if self.sports24_id:
        #    for yayin in safeiter(sports24.itermedias(self.sports24_id)):
        #        yield yayin

    def iterprogrammes(self):
        if self.yayin_id or self.yayin_name:
            for prog in yayinakisi.iterprogrammes(self.yayin_name, self.yayin_id):
                yield prog
        if self.vercel_id:
            for prog in vercel.iterprogrammes(self.vercel_id):
                yield prog
        if self.mynet_yayin:
            for prog in mynetyayin.iterprogrammes(self.mynet_yayin):
                yield prog
