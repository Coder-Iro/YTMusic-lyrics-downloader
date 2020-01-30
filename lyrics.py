from mutagen.id3 import ID3,USLT
import sys

fil = ID3(sys.argv[1])
with open(sys.argv[2],'r') as f:
    fil.add(USLT(encoding=3,text=f.read()))
fil.save()
