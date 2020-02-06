#!/usr/bin/env python3.8
import json
import os
from subprocess import Popen

import webvtt
import youtube_dl
from mutagen.id3 import ID3, SLT, APIC, TIT2, TPE1, TIT3

musicname = ''
lyricsname = ''
thumbsname = ''
metaname = ''

def hoook(d):
    global musicname
    global lyricsname
    global thumbsname
    global metaname
    if d['status'] == 'finished':
        musicname = d['filename'].replace(".webm",".mp3")
        lyricsname = d['filename'].replace(".webm",".ko.vtt")
        thumbsname = d['filename'].replace(".webm",".jpg")
        metaname = d['filename'].replace(".webm",".info.json")

def conv_to_ms(times):
    time = [int(x) for x in times.replace(".", ":").split(":")]
    ms = time[-1]+1000*time[-2]+1000*60*time[-3]+1000*60*60*time[-4]
    return ms

ydl_opts = {
        'format' : 'bestaudio/best',
        'extractaudio' : True,
        'audioformat' : 'mp3',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '0'
            },],
        'writeinfojson' : True,
        'writethumbnail' : True,
        'writesubtitles' : True,
        'subtitlesformat' : 'vtt',
        'subtitleslangs' : ['ko'],
        'progress_hooks' : [hoook],
        'prefer_ffmpeg' : True,
        }
ydl = youtube_dl.YoutubeDL(ydl_opts)

def download(url):
    ydl.download([url])
    fil = ID3(musicname)
    if os.path.isfile(lyricsname):
        lyrics = webvtt.read(lyricsname)
        lyri = [('',0)]
        for lyric in lyrics:
            lyri.append((lyric.text,conv_to_ms(lyric.start)))
            lyri.append(("",conv_to_ms(lyric.end)))
        tag = SLT(encoding=3, lang='kor', format=2, type=1, text=lyri)
        fil.add(tag)
        Popen(f'ffmpeg.exe -i "{lyricsname}" "{lyricsname.replace(".vtt", ".lrc")}"', shell=True).wait()
    fil.add(APIC(encoding=3, mime='image/jpeg', data=open(thumbsname,"rb").read()))
    with open(metaname, 'r') as f:
        meta = json.load(f)
    fil.add(TIT2(encoding=3, text=meta["title"]))
    fil.add(TIT3(encoding=3, text=meta["description"]))
    fil.add(TPE1(encoding=3, text=meta["uploader"]))
    fil.save(v1=0)
    os.remove(thumbsname)
    os.remove(lyricsname)
    os.remove(metaname)
    return musicname

if __name__ == "__main__":
    import sys
    os.chdir("dl")
    download(sys.argv[1])
