import re


def iteryoutube(self, url, headers=None):
    page = self.download(url, headers=headers)
    for video in re.finditer(r"hlsManifestUrl\\\":\\\"(.+?)\\\"", page):
        yield video.group(1).replace("\\", "")
