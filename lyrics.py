import traceback
import json
import os
import sys
from typing import List, Tuple

import webvtt
import youtube_dl
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TIT3, ID3v1SaveOptions, TALB
from webptools import dwebp

songlist: List[Tuple[str, str, str, str, str, str]] = []
lrcformat = '''[ti:{title}]
[ar:{artist}]
[la:KO]

'''


def safe_delete(filename):
    if os.path.exists(filename):
        os.remove(filename)


def hoook(d):
    if d['status'] == 'finished':
        filebase = ".".join(d['filename'].split(".")[:-1])
        musicnam = filebase + ".mp3"
        subnam = filebase + ".ko.vtt"
        orgthumbsnam = filebase + ".webp"
        thumbsnam = filebase + ".jpg"
        metanam = filebase + ".info.json"
        lyricsnam = filebase + ".lrc"
        global songlist
        songlist.append((musicnam, subnam, thumbsnam, metanam, orgthumbsnam, lyricsnam))


def conv_to_ms(times):
    time = [int(x) for x in times.replace(".", ":").split(":")]
    ms = "[{0:02d}:{1:02d}.{2:02d}]".format(time[-4] * 60 + time[-3], time[-2], (time[-1] // 10))
    return ms


YDL_OPTS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3'
    }, ],
    'writeinfojson': True,
    'writethumbnail': True,
    'writesubtitles': True,
    'subtitlesformat': 'vtt',
    'subtitleslangs': ['ko'],
    'progress_hooks': [hoook],
    'prefer_ffmpeg': True,
    'ignoreerrors': True,
}
ydl = youtube_dl.YoutubeDL(YDL_OPTS)
if __name__ == '__main__':
    ydl.download(sys.argv[1:])
    for musicname, subname, thumbsname, metaname, orgthumbsname, lyricsname in songlist:
        try:
            if os.path.exists(orgthumbsname):
                output = dwebp(orgthumbsname, thumbsname, "-o")
                if output["exit_code"] != 0:
                    print(output["stdout"].decode("UTF-8"))
                    print(output["stderr"].decode("UTF-8"))
            fil = ID3(musicname)
            with open(thumbsname, "rb") as f:
                fil.add(APIC(encoding=3, mime='image/jpeg', data=f.read()))
            with open(metaname, 'r') as f:
                meta = json.load(f)
            if os.path.exists(subname):
                lyri = ""
                lyrics = webvtt.read(subname)
                for lyric in lyrics:
                    lyri += conv_to_ms(lyric.start) + lyric.text.replace("\n", " ") + "\n"
                lyri = (lrcformat.format(title=meta["title"], artist=meta["uploader"]) + lyri).rstrip("\n")
                with open(lyricsname, "w") as f:
                    f.write(lyri)
                safe_delete(subname)
            fil.add(TIT2(encoding=3, text=meta["title"]))
            fil.add(TALB(encoding=3, text=meta["title"]))
            fil.add(TIT3(encoding=3, text=meta["description"]))
            fil.add(TPE1(encoding=3, text=meta["uploader"]))
            fil.save(v1=ID3v1SaveOptions.UPDATE)
            safe_delete(orgthumbsname)
            safe_delete(thumbsname)
            safe_delete(metaname)
        except Exception as e:
            print(f"Error occurs on {musicname}", file=sys.stderr)
            traceback.print_exc()
