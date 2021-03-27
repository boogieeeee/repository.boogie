# -*- encoding: utf-8 -*-
from liblivechannels.chexts.scrapertools.yayinakisi import yayinakisi
from liblivechannels.chexts.scrapertools.youtube import youtube
from liblivechannels.chexts.scrapertools import selcuk
from liblivechannels.chexts.scrapertools import ses


class multi(yayinakisi, youtube):
    yayin_id = None
    selcuk_name = None
    ses_id = None
    youtube_chanid = None
    youtube_stream = None
    youtube_sindex = None
    yayin_name = None
    yayin_id = None
    ses_ids = None

    def get(self):
        if self.ses_id or self.ses_ids:
            for yayin in ses.itermedias(self.ses_id, self.ses_ids):
                yield yayin
        if self.selcuk_name:
            for yayin in selcuk.itermedias(self.selcuk_name):
                yield yayin
        if self.youtube_chanid:
            for yayin in self.iteryoutube():
                yield yayin
