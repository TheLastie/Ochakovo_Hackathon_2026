from pathlib import Path
import json,subprocess,argparse,re
import cv2
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('role');p.add_argument('--ffmpeg',required=True);a=p.parse_args();D=R/a.role;v=D/f'export/{a.role}-mikhalych.mp4';c=cv2.VideoCapture(str(v));n=int(c.get(7));fps=c.get(5);size=[int(c.get(3)),int(c.get(4))];assert n==720 and fps==24 and size==[1280,720]
q=subprocess.run([a.ffmpeg,'-hide_banner','-v','error','-i',str(v),'-f','null','-'],capture_output=True,text=True);assert q.returncode==0,q.stderr
q=subprocess.run([a.ffmpeg,'-hide_banner','-i',str(v),'-af','volumedetect','-vn','-f','null','-'],capture_output=True,text=True);levels={key:float(re.search(key+r': ([\-\d.]+)',q.stderr).group(1)) for key in ['mean_volume','max_volume']};assert levels['max_volume']<0
sheet=Image.new('RGB',(1280,816),'white');draw=ImageDraw.Draw(sheet)
for i,t in enumerate([.4,1.5,3.3,5.4,7.8,10,12.5,14.2,16.3,19.8,23.8,28.7]):
 c.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=c.read();assert ok
 if i==2:cv2.imwrite(str(D/'export/poster.jpg'),f)
 im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB));im.thumbnail((320,180));x=i%4*320;y=i//4*272;sheet.paste(im,(x,y+24));draw.text((x,y+5),f'{t}s',fill='black')
sheet.save(D/'export/storyboard.jpg');c.release()
j={'duration':n/fps,'frames':n,'fps':fps,'size':size,'full_decode_passed':True,**levels,'asr':json.loads((D/'source/narration-asr.json').read_text())['transcript'],'review':'Visual contact sheet generated; audience testing not performed'};(D/'export/qa.json').write_text(json.dumps(j,ensure_ascii=False,indent=2));print(a.role,j)
