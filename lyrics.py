from mutagen.id3 import ID3, USLT, SLT
import sys
import webvtt

lyrics = webvtt.read(sys.argv[2])
lyri = []
lyr = []
for lyric in lyrics:
    times = [int(x) for x in lyric.start.replace(".", ":").split(":")]
    ms = times[-1]+1000*times[-2]+1000*60*times[-3]+1000*60*60*times[-4]
    lyri.append((lyric.text,ms))
    lyr.append(lyric.text)
fil = ID3(sys.argv[1])
tag = USLT(encoding=3, lang='kor', text="\n".join(lyr)) # this is unsynced lyrics
#tag = SLT(encoding=3, lang='kor', format=2, type=1, text=lyri) --- not working
print(tag)
fil.add(tag)
fil.save(v1=0)
