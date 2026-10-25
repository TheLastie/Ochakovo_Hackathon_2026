"""Build review boards from the current desktop gameplay screenshots."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, html
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'docs/game/gameplay/chemist-storyboard'
frames=json.loads((OUT/'frames.json').read_text())
font_path=ROOT/'tmp/defense-build/ProximaNova-Bold.ttf'
def font(size):return ImageFont.truetype(str(font_path) if font_path.exists() else '/System/Library/Fonts/Supplemental/Arial.ttf',size)
def board(ids,name,cols=3,width=720):
 gap=24;h=round(width*10/16);row=h+88;im=Image.new('RGB',(gap+(width+gap)*cols,140+((len(ids)+cols-1)//cols)*row),'white');d=ImageDraw.Draw(im);d.rectangle((24,24,im.width-24,30),fill='#D50032');d.text((24,44),'Завод → оборудование → завод',font=font(38),fill='#151515');d.text((24,96),'Химик-лаборант · ритм станций и приближённые головоломки · макет для Unity',font=font(20),fill='#62625F')
 for j,i in enumerate(ids):
  x=gap+(j%cols)*(width+gap);y=140+(j//cols)*row;shot=Image.open(OUT/'screens'/f'{i+1:02}.png').convert('RGB').resize((width,h),Image.Resampling.LANCZOS);im.paste(shot,(x,y));d.text((x,y+h+8),f'{i+1:02}  '+frames[i]['title'],font=font(25),fill='#151515');d.text((x,y+h+43),frames[i]['mode'],font=font(18),fill='#D50032')
 im.save(OUT/name,optimize=True)
board(list(range(len(frames))),'contact-sheet.png');board([0,3,4,5,7,10],'keyframes.png',2,800)
cards=[]
for i,f in enumerate(frames):
 e=html.escape;cards.append(f'<article><a href="index.html?frame={i+1}"><img src="screens/{i+1:02}.png" loading="lazy" alt="{e(f["title"])}"></a><p class="eyebrow">{i+1:02} · {e(f["mode"])}</p><h2>{e(f["title"])}</h2><p><b>Действие.</b> {e(f["action"])}</p><p><b>Почему так.</b> {e(f["reason"])}</p><p><b>Проверяем.</b> {e(f["check"])}</p></article>')
(OUT/'gallery.html').write_text('''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>12 кадров смены — макет Unity</title><link rel="stylesheet" href="style.css"><style>.grid{display:grid;grid-template-columns:1fr 1fr;gap:40px 28px}article img{width:100%}article h2{margin:10px 0}article p{font-size:17px}@media(max-width:850px){.grid{grid-template-columns:1fr}}</style><main><a href="index.html">← Играть и смотреть по кадрам</a><h1>Как проходит смена</h1><p>Общий вид, подход к станции, приближённая головоломка и возвращение в завод.</p><p><a href="contact-sheet.png">Все кадры одним листом</a> · <a href="../unity-gameplay.md">Спецификация Unity</a></p><section class="grid">'''+''.join(cards)+'''</section><p class="note">Макет взаимодействий, не готовая Unity-игра. Учебные данные не являются нормативами компании.</p></main></html>''')
print('BOARDS_READY',len(frames))
