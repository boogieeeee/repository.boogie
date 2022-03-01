# -*- encoding: utf-8 -*-
from liblivechannels.chexts.scrapertools import youtube
from liblivechannels.chexts.scrapertools import selcuk
from liblivechannels.chexts.scrapertools import ses
from liblivechannels.chexts.scrapertools import kolaytv
from liblivechannels.chexts.scrapertools import canlitvcenter
from liblivechannels.chexts.scrapertools import dadylive
from liblivechannels.chexts.scrapertools import sports24

from liblivechannels.chexts.scrapertools import yayinakisi
from liblivechannels.chexts.scrapertools import vercel
from liblivechannels.chexts.scrapertools import mynetyayin

from tinyxbmc.tools import safeiter


class multi:
    # kolay tv
    kolay_id = None
    kolay_ids = None

    # selcuk sports
    selcuk_name = None
    selcuk_mobile = None
    selcuk_adaptive = True
    selcuk_mobile_adaptive = False

    # youtube
    youtube_chanid = None
    youtube_stream = None
    youtube_sindex = None

    # ses tv
    ses_id = None
    ses_ids = None
    ses_adaptive = True

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
        if self.youtube_chanid:
            for yayin in safeiter(youtube.itermedias(self.youtube_chanid, self.youtube_stream, self.youtube_sindex)):
                yield yayin
        if self.kolay_id or self.kolay_ids:
            for yayin in safeiter(kolaytv.itermedias(self.kolay_id, self.kolay_ids)):
                yield yayin
        if self.canlitv_id or self.canlitv_ids:
            for yayin in safeiter(canlitvcenter.itermedias(self.canlitv_id, self.canlitv_ids)):
                yield yayin
        if self.dady_id or self.dady_name:
            for yayin in safeiter(dadylive.itermedias(self.dady_id, self.dady_name)):
                yield yayin
        if self.selcuk_name:
            for yayin in safeiter(selcuk.itermedias(self.selcuk_name, self.selcuk_adaptive)):
                yield yayin
        if self.ses_id or self.ses_ids:
            for yayin in safeiter(ses.itermedias(self.ses_id, self.ses_ids, self.ses_adaptive)):
                yield yayin
        if self.selcuk_mobile:
            for yayin in safeiter(selcuk.mobile_itermedias(self.selcuk_mobile, self.selcuk_mobile_adaptive)):
                yield yayin
        if self.sports24_id:
            for yayin in safeiter(sports24.itermedias(self.sports24_id)):
                yield yayin

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
