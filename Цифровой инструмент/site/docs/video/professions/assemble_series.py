"""Reproducible 30-second profession films: Flow shots, approved voice settings, kinetic type."""
from pathlib import Path
import argparse,json,subprocess,wave
import numpy as np
import soundfile as sf
from fontTools.ttLib import TTFont
R=Path(__file__).resolve().parent;ROOT=R.parents[2]
P=argparse.ArgumentParser();P.add_argument('role',choices=['bottling','machinery','brewer']);P.add_argument('--ffmpeg',required=True);A=P.parse_args();role=A.role;D=R/role;cfg=json.loads((R/'series.json').read_text())[role]
W=ROOT/'tmp/profession-films-review'/('edit-'+role);W.mkdir(parents=True,exist_ok=True);(D/'export').mkdir(exist_ok=True)
for n in ['Stratos-ExtraBold','ProximaNova-Bold']:
 f=TTFont(ROOT/f'brand/assets/fonts/{n}.woff2');f.flavor=None;f.save(W/f'{n}.ttf')
# A fixed low-level original percussion bed, not a generated or licensed song.
sr=48000;N=sr*30;t=np.arange(N)/sr;bed=np.zeros(N);rng=np.random.default_rng(2410)
for beat in np.arange(.12,27.8,60/112):
 i=int(beat*sr);n=min(int(.26*sr),N-i);u=np.arange(n)/sr
 bed[i:i+n]+=.15*np.sin(2*np.pi*(48*u+12*(1-np.exp(-u*23))/23))*np.exp(-u*24)
for beat in np.arange(.12,27.8,30/112):
 i=int(beat*sr);n=min(int(.045*sr),N-i);u=np.arange(n)/sr;noise=rng.normal(0,1,n);noise=np.diff(noise,prepend=0)
 bed[i:i+n]+=.012*noise*np.exp(-u*105)
bed*=np.minimum(1,t/.3)*np.clip((28-t)/.7,0,1);bed*=.026/max(np.sqrt(np.mean(bed**2)),1e-6)
sf.write(W/'rhythm.wav',bed,sr)
# Each tuple: source (1-based), source in/out, timeline out, purpose, optional crop.
if role=='bottling':
 S=[(1,2,2.7,.75,'bottle rhythm'),(1,2.7,4,2.25,'flow'),(1,0,1.95,4.5,'Mikhalych introduces'),(2,0,2,6.5,'sensor'),(1,4,6,8.95,'guarded mechanisms'),(2,4,5.6,10.5,'watch line'),(2,2,3.7,11.7,'panel'),(3,4.55,5.95,13.2,'check branded filled packaging'),(4,0,1.2,14.4,'notice warning'),(4,2,3.35,15.85,'consult instructions'),(5,.2,1.6,17.25,'report to Mikhalych'),(5,.1,1.6,18.75,'mentor demonstrates'),(5,2,3.8,20.5,'young operator acts'),(3,4.55,5.95,22,'finished branded kvass'),(3,4.55,5.95,23.65,'recognizable finished product'),(3,4.55,5.95,25.2,'branded product result'),(1,4.1,5.8,26.7,'confident work'),(1,0,1.3,28,'Mikhalych invitation')]
 intro=(2.25,4.5);knowledge=(4.5,8.95);tasks=(8.95,13.2);decision=(13.2,17.25);mentor=(17.25,20.5);result=(20.5,24);cta=(24,28)
elif role=='machinery':
 S=[(1,2,3,.8,'gauge'),(1,3,4,2.25,'scale of installation'),(1,0,2,4.4,'Mikhalych introduces'),(2,0,2,6.2,'read diagram'),(2,2,4,7.7,'compare indicator'),(2,4,5.6,9.15,'guarded mechanism'),(3,1,1.95,10.6,'check instruments'),(3,2,3.5,12,'observe mode'),(3,4,5.6,13.5,'operate panel'),(4,0,1.5,15,'notice changed trend'),(4,2,3.5,16.5,'consult instruction'),(4,4,5.6,18,'report'),(5,0,1.6,19.6,'Mikhalych explains'),(5,2,3.6,21.2,'trainee applies'),(1,4,5.4,22.6,'plant works'),(3,2.2,3.7,24.65,'control mode'),(5,4,5.6,26.3,'team result'),(1,0,1.7,28,'invitation')]
 intro=(2.25,4.4);knowledge=(4.4,9.15);tasks=(9.15,13.5);decision=(13.5,18);mentor=(18,21.2);result=(21.2,24.65);cta=(24.65,28)
else:
 S=[(3,0,1,.9,'amber kvass'),(3,1,2,2.4,'rare craft'),(3,2,4,4.35,'Mikhalych introduces'),(4,0,1.6,6,'technology'),(4,2,3.4,7.5,'fermentation observation'),(1,0,1.4,8.9,'grain and malt'),(1,0,1.4,10.25,'check grain and malt'),(4,4,5.4,11.6,'monitor fermentation'),(1,4,5.4,13,'record'),(5,0,1.5,14.5,'notice trend'),(5,2,3.5,16.2,'consult journal'),(2,0,1.5,17.7,'discuss finding'),(5,4,5.6,19.4,'compare instruction'),(2,1.5,3,21,'Mikhalych explains'),(2,3.2,4.6,22.45,'young brewer records'),(2,4.6,5.9,23.85,'apply independently'),(3,4,5.3,25.2,'finished kvass'),(1,2,3.3,26.55,'personal contribution'),(3,2,3.5,28,'invitation')]
 intro=(2.4,4.35);knowledge=(4.35,8.9);tasks=(8.9,13);decision=(13,19.4);mentor=(19.4,23.85);result=(23.85,26.55);cta=(26.55,28)
source_files=[D/f'source/{i:02}-flow.mp4' for i in range(1,6)]
if role=='bottling':source_files[2]=D/'source/06-branded.mp4'
if role=='brewer':source_files[2]=D/'source/03-branded-intro.mp4'
F=[];timeline=[];cursor=0
for i,(source,si,so,end,purpose,*extra) in enumerate(S):
 end=round(end*24)/24;frames=round((end-cursor)*24);span=frames/24
 F.append(f'[{source-1}:v]trim=start={si}:end={so},setpts=(PTS-STARTPTS)*{span/(so-si)},fps=24,tpad=stop_mode=clone:stop_duration=0.12,trim=end_frame={frames},setpts=PTS-STARTPTS,scale=1280:720,setsar=1[v{i}]')
 timeline.append({'start':cursor,'end':end,'source':str(source_files[source-1].relative_to(D)),'in':si,'out':so,'purpose':purpose});cursor=end
F.append('[5:v]trim=end_frame=48,setpts=PTS-STARTPTS,setsar=1[card]');F.append(''.join(f'[v{i}]' for i in range(len(S)))+f'[card]concat=n={len(S)+1}:v=1:a=0[film]')
v=[];typo=[]
def enable(a,b):return f'gte(t,{a})*lt(t,{b})'
def box(x,y,w,h,c,a,b):v.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color={c}:t=fill:enable='{enable(a,b)}'")
def txt(s,a,b,size=52,x=64,y=580,color='0x151515',font='Stratos-ExtraBold',slide=True):
 p=W/f'type-{len(v)}.txt';p.write_text(s);xx=f'{x}+22*max(0,1-(t-{a})/.16)' if slide and isinstance(x,int) else x
 v.append(f"drawtext=fontfile='{W/(font+'.ttf')}':textfile='{p}':fontsize={size}:fontcolor={color}:x='{xx}':y={y}:enable='{enable(a,b)}'");typo.append({'text':s,'start':a,'end':b,'size':size})
def fit_size(s,base=38,max_width=478):
 font=TTFont(W/'ProximaNova-Bold.ttf');cmap=font.getBestCmap();width=sum(font['hmtx'][cmap.get(c,'space')][0] for c in s)/font['head'].unitsPerEm
 return min(base,int(max_width/max(width,.01)))
def tag(s,a,b,num=None,right=False):
 x=700 if right else 54;box(x,554,526,118,'white@.96',a,b);box(x,554,7,118,'0xD50032',a,b)
 if num:txt(num,a,b,24,x+23,568,'0xD50032','ProximaNova-Bold')
 txt(s,a,b,fit_size(s),x+23,608 if num else 590,font='ProximaNova-Bold')
# Hook: two distinct typographic scales, then the title in the presenter's clean left field.
box(40,492,710,183,'black@.55',0,intro[0]);txt(cfg['hook'][0].upper(),0,intro[0],44,64,515,'white');txt(cfg['hook'][1].upper(),.72,intro[0],67,60,579,'white')
a,b=intro;box(0,0,720,720,'white@.97',a,b);box(54,166,76,8,'0xD50032',a,b);txt('ПРОФЕССИИ ОЧАКОВО',a,b,25,54,202,'0xD50032','ProximaNova-Bold')
for j,line in enumerate(cfg['title_lines']):txt(line,a,b,62 if len(line)<14 else 54,50,278+80*j)
# Persistent tiny employer name. Key words remain brief, not full subtitles.
box(1010,28,232,42,'white@.92',b,28);txt('ОЧАКОВО',b,28,26,1040,36,'0xD50032','ProximaNova-Bold',False)
a,b=knowledge;mid=a+(b-a)*.58;tag(cfg['knowledge'][0],a,mid,'ПРИГОДИТСЯ');tag(cfg['knowledge'][1],mid,b,'ПРИГОДИТСЯ',True)
a,b=tasks
for i,s in enumerate(cfg['tasks']):
 lo=a+(b-a)*i/3;hi=a+(b-a)*(i+1)/3;tag(s,lo,hi,f'0{i+1}  /  В ДЕЛЕ',(i==1 or (role=='bottling' and i==2)))
a,b=decision;mid=a+(b-a)*.33
box(54,62,605,122,'0xD50032',a,mid);txt('А ЕСЛИ СБОЙ?' if role=='bottling' else 'ПОКАЗАНИЯ ИЗМЕНИЛИСЬ?',a,mid,43 if role=='bottling' else 33,78,98,'white')
tag(cfg['decision'][1],mid,a+(b-a)*.68,'ПРОВЕРЬ');tag(cfg['decision'][2],a+(b-a)*.68,b,'ДЕЙСТВУЙ',True)
a,b=mentor;mid=(a+b)/2;tag('Учиться у опытных',a,mid,'МИХАЛЫЧ РЯДОМ');tag('Применять самому',mid,b,'ТВОЙ ХОД',True)
a,b=result;box(650,516,576,156,'white@.96',a,b);txt('ТВОЙ ВКЛАД',a,b,25,674,534,'0xD50032','ProximaNova-Bold');words={'bottling':['Готовые напитки','Ровным потоком'],'machinery':['Производство','работает стабильно'],'brewer':['Качество','знакомого кваса']}[role]
txt(words[0],a,b,48,670,576);txt(words[1],a+.28,b,36,674,636,'0xD50032','ProximaNova-Bold')
a,b=cta;tag('Хочешь попробовать?',a,b,'ТВОЙ СЛЕДУЮЩИЙ ШАГ',True)
box(72,120,90,8,'0xD50032',28,30);txt('ОЧАКОВО',28,30,28,72,166,'0xD50032','ProximaNova-Bold');txt('Твои знания',28,30,83,66,265);txt('нужны в деле',28.15,30,83,66,355);box(72,515,540,83,'0xD50032',28,30);txt('Узнай о практике',28,30,43,101,533,'white','ProximaNova-Bold')
F.append('[film]'+','.join(v)+',format=yuv420p[typed]');F.append('[8:v]scale=-1:570,format=rgba[pack]');F.append("[typed][pack]overlay=x=940:y=100:enable='gte(t,28)',format=yuv420p[final]");F.append('[6:a]loudnorm=I=-16:TP=-1.5:LRA=7,apad=pad_dur=4[voice]');F.append('[7:a]volume=.27[bed]');F.append('[voice][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=.84:level=false[audio]')
(W/'filters.txt').write_text(';'.join(F));out=D/f'export/{role}-mikhalych.mp4'
cmd=[A.ffmpeg,'-hide_banner','-loglevel','warning','-y']
for source_file in source_files:cmd+=['-i',str(source_file)]
cmd+=['-f','lavfi','-i','color=c=white:s=1280x720:r=24:d=2','-i',str(D/'source/narration.wav'),'-i',str(W/'rhythm.wav'),'-loop','1','-i',str(R/'shared/ochakovsky-05-official.png'),'-filter_complex_script',str(W/'filters.txt'),'-map','[final]','-map','[audio]','-t','30','-r','24','-fps_mode','cfr','-c:v','libx264','-crf','18','-preset','medium','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
(D/'export/edit.json').write_text(json.dumps({'role':role,'title':cfg['title'],'duration':30,'fps':24,'size':[1280,720],'timeline':timeline,'typography':typo,'narration':json.loads((D/'source/narration.json').read_text()),'audio':'Approved greeting-based narration, original low-level percussion bed; Flow source audio discarded','status':'Complete review film; audience impact not measured'},ensure_ascii=False,indent=2))
print(out)
