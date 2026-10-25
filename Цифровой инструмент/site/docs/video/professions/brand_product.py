"""Composite the genuine product label into stable frontal planes of the Flow video.
Video compositing only. Original source image and raw Flow take remain untouched.
"""
from pathlib import Path
import cv2,numpy as np,subprocess,json
R=Path(__file__).resolve().parent;ROOT=R.parents[2];ff=ROOT/'tmp/mikhalych-flow-2026-10-16/tools/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
src=R/'bottling/source/06-flow.mp4';out=R/'bottling/source/06-branded.mp4'
photo=cv2.imread(str(R/'shared/ochakovsky-05-official.png'),cv2.IMREAD_UNCHANGED)
label=photo[354:654,43:374,:3];h,w=label.shape[:2];shade=(.84+.16*np.sin(np.linspace(0,np.pi,w)))*.94;label=np.clip(label.astype(float)*shade[None,:,None],0,255).astype(np.uint8);source=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
quads=[np.float32([[341,460],[470,460],[469,605],[339,605]]),np.float32([[477,460],[604,460],[604,605],[475,605]])]
cap=cv2.VideoCapture(str(src));proc=subprocess.Popen([str(ff),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
ref=None;points=None;idx=0
while True:
 ok,frame=cap.read()
 if not ok:break
 t=idx/24
 if t>=4.5:
  gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
  if ref is None:
   ref=gray;mask=np.zeros_like(gray);mask[450:616,330:615]=255;points=cv2.goodFeaturesToTrack(gray,80,.01,8,mask=mask)
  nxt,status,err=cv2.calcOpticalFlowPyrLK(ref,gray,points,None)
  a=points[status.flatten()==1];b=nxt[status.flatten()==1];shift=np.median((b-a).reshape(-1,2),axis=0) if len(a)>5 else np.zeros(2)
  for q in quads:
   target=q+shift;H=cv2.getPerspectiveTransform(source,target);overlay=cv2.warpPerspective(label,H,(1280,720));overlay=cv2.GaussianBlur(overlay,(3,3),.65);alpha=cv2.warpPerspective(np.full((h,w),255,np.uint8),H,(1280,720));alpha=cv2.GaussianBlur(cv2.erode(alpha,np.ones((3,3),np.uint8)),(5,5),.9).astype(float)/255
   frame=(frame*(1-alpha[:,:,None])+overlay*alpha[:,:,None]).astype(np.uint8)
 proc.stdin.write(frame.tobytes());idx+=1
proc.stdin.close();assert proc.wait()==0;cap.release()
(R/'bottling/source/brand-composite.json').write_text(json.dumps({'raw_video':'06-flow.mp4','output':'06-branded.mp4','official_label_image':'../../shared/ochakovsky-05-official.png','source_label_rectangle':[43,354,374,654],'tracked_front_labels_from_seconds':4.5,'selected_in_final_film':'4.55–5.95 seconds only; generated front labels replaced by original raster','tracking':'Median Lucas-Kanade optical-flow translation of two frontal label planes'},ensure_ascii=False,indent=2))
# Product-specific intro: genuine composited product planes + the existing drawn presenter.
old=R/'brewer/source/03-flow.mp4';new=R/'brewer/source/03-branded-intro.mp4'
filters='[0:v]trim=start=4.55:end=5.95,setpts=(PTS-STARTPTS)*2/1.4,fps=24,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame=48,crop=850:478:220:242,scale=1280:720,setsar=1[a];[1:v]trim=start=2:end=4,setpts=PTS-STARTPTS,fps=24,trim=end_frame=48,setsar=1[b];[0:v]trim=start=4.55:end=5.95,setpts=(PTS-STARTPTS)*2/1.4,fps=24,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame=48,setsar=1[c];[a][b][c]concat=n=3:v=1:a=0[v]'
subprocess.run([str(ff),'-v','error','-y','-i',str(out),'-i',str(old),'-filter_complex',filters,'-map','[v]','-an','-r','24','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(new)],check=True)
print(out,new)
