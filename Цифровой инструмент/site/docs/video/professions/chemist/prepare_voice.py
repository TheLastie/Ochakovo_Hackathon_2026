"""Remove 0.52s of verified inter-sentence silence; never stretch speech or shift pitch."""
from pathlib import Path
import json
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent/'source'
a,sr=sf.read(R/'narration-raw.wav');assert abs(len(a)/sr-30.08)<.15, 'Reference take changed: verify quiet intervals before trimming';cuts=[(4.90,5.10),(9.58,9.76),(14.13,14.27)]
parts=[];cursor=0
for start,end in cuts:
 parts.append(a[cursor:round(start*sr)].copy());cursor=round(end*sr)
parts.append(a[cursor:].copy())
# Tiny fades fall wholly inside the retained silence on each side of a join.
n=round(.005*sr)
for i,part in enumerate(parts):
 if i:part[:n]*=np.linspace(0,1,n)
 if i<len(parts)-1:part[-n:]*=np.linspace(1,0,n)
out=np.concatenate(parts);sf.write(R/'narration.wav',out,sr)
d=json.loads((R/'narration-raw.json').read_text());d['raw_duration']=len(a)/sr;d['duration']=len(out)/sr;d['pause_trims_seconds']=cuts;d['removed_inter_sentence_silence_seconds']=sum(e-s for s,e in cuts);d['word_timing_stretched']=False;d['speed_change']=False;d['pitch_shift_semitones']=0
(R/'narration.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));print(json.dumps(d,ensure_ascii=False))
