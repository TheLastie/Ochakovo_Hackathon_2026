"""Render Flow shots with the approved mentor voice and a clean, consistent web export."""
from pathlib import Path
import subprocess,json,shutil
ROOT=Path(__file__).resolve().parents[3]
D=Path(__file__).resolve().parent
FF=ROOT/'tmp/mikhalych-flow-2026-10-16/tools/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
OUT=D/'export';OUT.mkdir(exist_ok=True)
# Speech windows from independent ASR of the Flow source audio, not generated lip-sync claims.
windows={'finale-01':(1.5,6.76),'finale-02':(0,6.68),'finale-03':(0,6.42),'unavailable':(0,6.94)}
report=[]
for name,(start,end) in windows.items():
 meta=json.loads((D/'source'/(name+'-voice.json')).read_text());duration=meta['duration'];ratio=duration/(end-start)
 vf=f'trim=start={start}:end={end},setpts={ratio}*(PTS-STARTPTS),tpad=start_mode=clone:start_duration=0.25:stop_mode=clone:stop_duration=0.65,fps=24,format=yuv420p'
 af='adelay=250:all=1,apad=pad_dur=0.65,loudnorm=I=-16:TP=-1.5:LRA=7,afade=t=in:d=0.03'
 dest=OUT/(name+'.mp4')
 subprocess.run([str(FF),'-y','-i',str(D/'source'/(name+'.mp4')),'-i',str(D/'source'/(name+'-voice.wav')),'-filter_complex',f'[0:v]{vf}[v];[1:a]{af}[a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','medium','-crf','19','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 report.append({'clip':name,'flowSpeechWindow':[start,end],'voiceDuration':duration,'pictureTimeScale':ratio,'nativeAudioUsed':False,'note':'Picture retimed to speech duration; mouth motion is approximate, not phoneme-aligned dubbing.'})
# Clean cuts between matching shots; a continuous voice was rendered with the same identity/settings.
concat=OUT/'concat.txt';concat.write_text('\n'.join("file '"+name+".mp4'" for name in ['finale-01','finale-02','finale-03'])+'\n')
subprocess.run([str(FF),'-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(OUT/'finale.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
public=ROOT/'web/public/videos/game';public.mkdir(parents=True,exist_ok=True)
for name in ['finale','unavailable']:
 shutil.copy2(OUT/(name+'.mp4'),public/(name+'.mp4'))
 src=D/'source'/('finale-01.jpg' if name=='finale' else 'unavailable.jpg');shutil.copy2(src,public/(name+'.jpg'))
(OUT/'edit.json').write_text(json.dumps({'renderer':'FFmpeg','source':'Google Flow Omni 1.1 Flash, 1280x720, 8 seconds per shot','voice':'Qwen3 TTS, exact previously approved fictional greeting reference, same seed/settings as profession films','clips':report},ensure_ascii=False,indent=2))
print('Rendered and copied final + unavailable videos to local website')
