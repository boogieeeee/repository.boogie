from tinyxbmc import tools
from tinyxbmc import addon

from liblivechannels import common
from six import PY2

import codecs


class write(addon.blockingloop):
    def init(self, base, progress=None):
        self.base = base
        self.wfile = u""
        self.progress = progress

    def oninit(self):
        self.channels = list(self.base.config.channels)
        self.index = 0
        self.writeline("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<!DOCTYPE tv SYSTEM \"xmltv.dtd\">\n<tv>\n")

    def onloop(self):
        try:
            icon, title, index, cats, _isdaptive = self.channels[self.index]
        except IndexError:
            self.writeline("</tv>")
            with codecs.open(common.epath, "w", encoding="utf-8") as f:
                f.write(self.wfile)
            self.base.config.update_pvr = True
            self.close()
            return
        self.index += 1
        if "Broken" in cats:
            return
        if self.progress:
            self.progress.update(int(100 * self.index / len(self.channels)), "Updating EPG: %s" % title)
        self.writeline('<channel id="%s">' % index)
        self.writeline('\t<display-name>%s</display-name>' % self.xmlescape(title))
        self.writeline('\t<icon src="%s"/>' % icon)
        self.writeline("</channel>")
        channel = self.base.loadchannel(index)
        if not channel:
            return
        for programme in tools.safeiter(channel.iterprogrammes()):
            if programme is None:
                continue
            self.writeline('<programme start="%s" stop="%s" channel="%s">' % (programme.start, programme.end, self.xmlescape(index)))
            self.writeline('\t<title>%s</title>' % self.xmlescape(programme.title))
            if programme.desc:
                self.writeline('\t<desc>%s</desc>' % self.xmlescape(programme.desc))
            for pcat in programme.categories:
                self.writeline('\t<category>%s</category>' % self.xmlescape(pcat))
            if programme.subtitle:
                self.writeline('\t<sub-title>%s</sub-title>' % self.xmlescape(programme.subtitle))
            if programme.airdate:
                self.writeline('\t<date>%s</date>' % programme.airdate)
            if programme.episode:
                self.writeline('\t<episode-num system="onscreen">%s</episode-num>' % self.xmlescape(programme.episode))
            if len(programme.directors) or len(programme.writers) or len(programme.actors):
                self.writeline('\t<credits>')
                for key, iterable in [("director", programme.directors),
                                      ("writer", programme.writers),
                                      ("actor", programme.actors)]:
                    for item in iterable:
                        self.writeline('\t\t<%s>%s</%s>' % (key, self.xmlescape(item), key))
                self.writeline('\t</credits>')
            if programme.icon:
                self.writeline('\t<icon src="%s"/>' % self.xmlescape(programme.icon))
            self.writeline('</programme>')

    def writeline(self, txt):
        if PY2 and isinstance(txt, unicode):
            txt.encode("utf-8")
        self.wfile += txt + "\n"

    def xmlescape(self, txt):
        for rep, char in [("&", "&amp;"), ("\"", "&quot;"), ("'", "&apos;"), ("<", "&lt;"), (">", "&gt;")]:
            txt = txt.replace(rep, char)
        return txt
