"""Derive cylindrical product textures from authentic official packshots.
The front uses inverse cylindrical projection. The unavailable rear is a plain
colour continuation, never invented legal text, barcodes, or a second front logo.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path(__file__).resolve().parent/'source'
OUT=ROOT/'OchakovoFactoryWorld/Assets/FactoryKit/Products/Textures'
OUT.mkdir(parents=True,exist_ok=True)
records=[]

def atlas(id,file,crop,background,metallic,smoothness,url,page,follow_silhouette=False):
    source=Image.open(SOURCE/file).convert('RGBA')
    image=np.array(source.convert('RGB'),dtype=float)
    x0,y0,x1,y1=crop
    h,w=1024,2048
    theta=((np.arange(w)+.5)/w-.5)*2*np.pi
    front=np.abs(theta)<=np.pi/2
    # Photo X is sin(angle) on the visible half of a cylinder.
    sx=np.clip((x0+x1)/2+(x1-x0)/2*np.sin(theta),x0,x1-1)
    sy=np.linspace(y0,y1-1,h)
    ya=sy.astype(int);yb=np.minimum(ya+1,image.shape[0]-1);yf=sy-ya
    if follow_silhouette:
        alpha=np.asarray(source)[:,:,3]
        left=[];right=[]
        for row in ya:
            opaque=np.where(alpha[row]>128)[0]
            left.append(max(x0,opaque.min()+2));right.append(min(x1-1,opaque.max()-2))
        left=np.array(left)[:,None];right=np.array(right)[:,None]
        sx=(left+right)/2+(right-left)/2*np.sin(theta)[None,:]
    else:sx=np.broadcast_to(sx,(h,w))
    xa=sx.astype(int);xb=np.minimum(xa+1,image.shape[1]-1);xf=sx-xa
    sampled=((1-yf[:,None,None])*((1-xf[:,:,None])*image[ya[:,None],xa]+xf[:,:,None]*image[ya[:,None],xb])+
             yf[:,None,None]*((1-xf[:,:,None])*image[yb[:,None],xa]+xf[:,:,None]*image[yb[:,None],xb]))
    out=np.zeros((h,w,3))+np.array(background)
    # Fade only the outermost unprinted edge into a neutral reverse surface.
    blend=np.clip((np.pi/2+.12-np.abs(theta))/.12,0,1)
    out=out*(1-blend[None,:,None])+sampled*blend[None,:,None]
    path=OUT/(id+'_Albedo.png');Image.fromarray(np.uint8(np.clip(out,0,255))).save(path,optimize=True)
    rng=np.random.default_rng(241024)
    packed=np.zeros((512,1024,4),dtype=np.uint8);packed[:,:,:3]=int(metallic*255)
    packed[:,:,3]=np.uint8(np.clip(smoothness+rng.normal(0,.006,(512,1024)),0,1)*255)
    Image.fromarray(packed).save(OUT/(id+'_MetallicSmoothness.png'),optimize=True)
    records.append({'id':id,'source':file,'source_url':url,'page':page,'accessed':'2026-10-24',
        'source_sha256':hashlib.sha256((SOURCE/file).read_bytes()).hexdigest(),'crop_pixels':crop,
        'atlas_pixels':[w,h],'method':'inverse cylindrical front projection; plain reverse continuation',
        'rights':'Official Ochakovo product artwork; not CC0; source retained without modification'})

atlas('Ochakovsky_Label','ochakovsky-official-pet.png',[43,354,367,653],[218,181,30],0,.48,
      'https://ochakovo.ru/wp-content/uploads/2024/09/ochak_05_p.png','https://ochakovo.ru/brand/ochakovskij/')
atlas('Mojito_Label','mojito-official-can.png',[61,26,369,758],[206,224,179],.12,.62,
      'https://ochakovo.ru/wp-content/uploads/2024/09/mohito-can.png','https://ochakovo.ru/brand/moxito-osvezhayushhij-4/',True)
(SOURCE/'provenance.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('PRODUCT_TEXTURES_READY',len(records))
