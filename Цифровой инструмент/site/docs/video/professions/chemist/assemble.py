"""Build the current career film from Flow footage and continuous Mikhalych narration."""
from pathlib import Path
import argparse,json,subprocess,wave
from fontTools.ttLib import TTFont
R=Path(__file__).resolve().parent;ROOT=R.parents[3]
p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default='ffmpeg');a=p.parse_args()
work=ROOT/'tmp/profession-films-review/edit';work.mkdir(parents=True,exist_ok=True)
for name in ['Stratos-ExtraBold','ProximaNova-Bold']:
 font=TTFont(ROOT/f'brand/assets/fonts/{name}.woff2');font.flavor=None;font.save(work/f'{name}.ttf')
with wave.open(str(R/'source/narration.wav')) as w:voice_duration=w.getnframes()/w.getframerate()
duration=30.0
assert voice_duration<30, f'Shorten narration naturally: {voice_duration}s'
# source index (0-based), original start/end, edited duration, purpose.
shots=[(2,1,2,1.25,'macro sample'),(0,2,4,1.75,'sample'),(0,0,2,2.1,'mentor presents role'),(2,2,4,1.7,'knowledge: calculation'),(2,4,6,2,'knowledge: measurement'),(0,2,4,1.2,'take sample'),(0,4,6,1.5,'analysis'),(1,0,2,1.5,'compare'),(3,0,2,1.5,'notice'),(3,2,4,1.5,'check graph'),(3,4,6,1.5,'report'),(4,.8,2.3,1.5,'experienced colleague'),(4,3.5,5,1.5,'young colleague acts'),(2,0,1,1.1,'attention'),(2,4,6,2.4,'skill'),(1,4,6,3,'Mikhalych invitation')]
frame_counts=[30,42,49,49,58,32,34,40,38,38,39,41,40,32,64,46]
shots=[(source,start,end,frame_counts[i]/24,purpose) for i,(source,start,end,span,purpose) in enumerate(shots)]
f=[];timeline=[];cursor=0
for i,(source,start,end,span,purpose) in enumerate(shots):
 crop='crop=1120:630:0:0,' if source==3 and start==4 else ''
 f.append(f'[{source}:v]trim=start={start}:end={end},setpts=(PTS-STARTPTS)*{span/(end-start)},fps=24,tpad=stop_mode=clone:stop_duration=0.08,trim=end_frame={frame_counts[i]},setpts=PTS-STARTPTS,{crop}scale=1280:720,setsar=1[v{i}]')
 timeline.append({'start':round(cursor,3),'end':round(cursor+span,3),'source':f'source/{source+1:02}-flow.mp4','source_in':start,'source_out':end,'purpose':purpose});cursor+=span
assert abs(cursor-28)<.001
f.append('[5:v]trim=duration=2,setpts=PTS-STARTPTS,setsar=1[card]')
f.append(''.join(f'[v{i}]' for i in range(len(shots)))+'[card]'+f'concat=n={len(shots)+1}:v=1:a=0[film]')
v=[]
def box(x,y,w,h,color,when):v.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color={color}:t=fill:enable='{when}'")
def text(content,font,size,x,y,color,when):
 target=work/f'long-text-{len(v)}.txt';target.write_text(content)
 v.append(f"drawtext=fontfile='{work/(font+'.ttf')}':textfile='{target}':fontsize={size}:fontcolor={color}:x={x}:y={y}:enable='{when}'")
def label(content,start,end,width=550):
 when=f'between(t,{start},{end-.042})';box(48,598,width,78,'white@0.96',when);box(48,598,7,78,'0xD50032',when);text(content,'ProximaNova-Bold',39,76,618,'0x151515',when)
label('Маленькая проба',0,1.25,430);label('Большая ответственность',1.25,3,670)
intro='between(t,3,5.000)';box(60,164,72,7,'0xD50032',intro)
text('ПРОФЕССИИ «ОЧАКОВО»','ProximaNova-Bold',24,60,196,'0xD50032',intro)
text('Химик-','Stratos-ExtraBold',66,56,264,'0x151515',intro);text('лаборант','Stratos-ExtraBold',66,56,342,'0x151515',intro)
label('Химия и концентрации',5.042,7.083,610);label('Точность измерений',7.083,9.5,570)
label('Отобрать пробу',9.5,10.833,450);label('Провести анализ',10.833,12.25,490);label('Сравнить с нормой',12.25,13.917,530)
label('Заметить отклонение',13.917,17.083,610);label('Передать результат команде',17.083,18.708,800)
label('Учиться у опытных',18.708,20.417,550);label('Применять самому',20.417,22.083,550)
label('Твоя точность сохраняет качество',22.083,26.083,890)
ending='between(t,26.083,27.958)';box(48,548,590,130,'white@0.96',ending);box(48,548,7,130,'0xD50032',ending)
text('Хочешь попробовать?','ProximaNova-Bold',40,76,570,'0x151515',ending);text('Узнай о практике','ProximaNova-Bold',40,76,620,'0xD50032',ending)
card='gte(t,28)';box(80,126,92,8,'0xD50032',card)
text('ОЧАКОВО · ХИМИК-ЛАБОРАНТ','ProximaNova-Bold',29,80,170,'0xD50032',card)
text('Твои знания','Stratos-ExtraBold',72,76,270,'0x151515',card);text('нужны в деле','Stratos-ExtraBold',72,76,356,'0x151515',card)
text('Узнай о практике','ProximaNova-Bold',43,80,514,'0xD50032',card)
f.append('[film]'+','.join(v)+',fps=24,format=yuv420p[final]');f.append('[6:a]loudnorm=I=-16:TP=-1.5:LRA=7,apad=pad_dur=4[audio]')
(work/'filters-long.txt').write_text(';'.join(f));out=R/'export/chemist-mikhalych.mp4'
cmd=[a.ffmpeg,'-hide_banner','-loglevel','warning','-y']
for i in range(1,6):cmd+=['-i',str(R/f'source/{i:02}-flow.mp4')]
cmd+=['-f','lavfi','-i','color=c=white:s=1280x720:r=24:d=2','-i',str(R/'source/narration.wav'),'-filter_complex_script',str(work/'filters-long.txt'),'-map','[final]','-map','[audio]','-t',str(duration),'-r','24','-fps_mode','cfr','-c:v','libx264','-crf','18','-preset','medium','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
report={'duration':duration,'narration_duration':voice_duration,'fps':24,'size':[1280,720],'source':'Google Flow, Omni 1.1 Flash, five 6-second production clips','flow_project':'https://flow.google.com/project/54d557a8-dda9-4f2a-a10e-1f4839ecd715','flow_asset_ids':['a705b4a7-854a-49c1-96ca-bc24e42a7b08','7ed746d0-4d15-4115-b862-c3f772bd8f7e','e3db4ea4-2616-408f-ae5e-a7d778857e7e','cd306000-c1a1-4c82-af8b-1a8b39a2d203','9530967e-125d-4d9a-9844-2f1d8964f2b8'],'credits_spent_before_mentor_revision':50,'credits_spent_expansion':30,'mentor_edit_credit_cost':'not displayed by direct editor','mentor_revision':{'type':'Photorealistic Mikhalych identity replacement','tool':'Built-in imagegen reference + Google Flow video edit','reference':'source/mentor-mikhalych-reference.png','prompt':'mentor-reference-prompt.txt','edit_parent_asset_id':'9530967e-125d-4d9a-9844-2f1d8964f2b8','downloaded_result':'Laborant_learning_pipetting_tech…_20261024005213.mp4','adjacent_shot':'Reframed tablet handover to exclude previous mentor at right edge'},'timeline':timeline,'end_card':[28,30],'voice_revision':json.loads((R/'source/narration.json').read_text()),'narration_speed_changed':False,'original_flow_audio_used':False,'fonts':['Stratos ExtraBold','Proxima Nova Bold'],'status':'Revised complete film awaiting user approval; replaces 13.5-second cut'}
(R/'export/edit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
subprocess.run([a.ffmpeg,'-loglevel','error','-y','-ss','3.8','-i',str(out),'-frames:v','1',str(R/'export/poster.jpg')],check=True)
print(json.dumps({'duration':duration,'narration':voice_duration,'shots':len(shots),'output':str(out)},ensure_ascii=False))
