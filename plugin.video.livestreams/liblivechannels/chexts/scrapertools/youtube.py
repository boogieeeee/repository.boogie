try:
    import unittest
    import test

    class testyt(unittest.TestCase):
        def test_yt_link(self):
            test.testlink(self, itermedias("@krtcanli", 0), 1, "bein1", 0)

except ImportError:
    pass

from tinyxbmc import mediaurl
import ghub
ghub.load("yt-dlp", "yt-dlp", "master")
import yt_dlp


def itermedias(chanid, sindex):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlist_items': str(sindex + 1),
        'playlistreverse': True,
        'force_generic_extractor': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/{chanid}/streams", download=False)
        if 'entries' in info and len(info['entries']) > 0:
            first = info['entries'][sindex]
            vinfo = ydl.extract_info(first["url"], download=False)
            yield mediaurl.HlsUrl(vinfo["url"])
