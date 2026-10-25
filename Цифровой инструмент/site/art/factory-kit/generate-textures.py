"""Deterministic, seamless original PBR surfaces. No external image dependencies.
Albedo is sRGB; Normal is tangent-space OpenGL; MetallicSmoothness is linear
with metallic in RGB and Unity Standard smoothness (1 - roughness) in alpha.
All maps represent a 1 x 1 metre surface, except compact props using source UVs.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'OchakovoFactoryWorld/Assets/FactoryKit/Textures/Surfaces'
OUT.mkdir(parents=True,exist_ok=True)
N=512
y,x=np.mgrid[0:N,0:N]/N
rng=np.random.default_rng(24102026)

def periodic(scale,seed):
    r=np.random.default_rng(seed)
    field=np.zeros((N,N))
    for _ in range(20):
        kx,ky=r.integers(-scale,scale+1,2)
        if kx==ky==0:continue
        field+=np.cos(2*np.pi*(kx*x+ky*y)+r.uniform(0,2*np.pi))
    return field/max(field.std(),.01)

coarse=periodic(4,5);medium=periodic(28,6);fine=periodic(170,7)
noise=rng.normal(size=(N,N))
records=[]

def save(name,albedo,height,roughness,metallic):
    albedo=np.clip(albedo,0,1)
    if albedo.ndim==2:albedo=np.repeat(albedo[...,None],3,2)
    dx=(np.roll(height,-1,1)-np.roll(height,1,1))*N/2
    dy=(np.roll(height,-1,0)-np.roll(height,1,0))*N/2
    # PNG rows run downwards; tangent-space V runs upwards.
    normal=np.stack([-dx,dy,np.ones_like(dx)],2)
    normal/=np.linalg.norm(normal,axis=2)[...,None]
    normal=normal*.5+.5
    roughness=np.clip(np.broadcast_to(roughness,(N,N)),.03,.98)
    metallic=np.clip(np.broadcast_to(metallic,(N,N)),0,1)
    combined=np.stack([metallic,metallic,metallic,1-roughness],2)
    maps={'Albedo':albedo,'Normal':normal,'MetallicSmoothness':combined,'Roughness':roughness}
    for suffix,array in maps.items():
        p=OUT/(name+'_'+suffix+'.png')
        Image.fromarray(np.uint8(np.clip(array,0,1)*255)).save(p,optimize=True)
        records.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})

# Continuous directional machining lines plus sparse, fine cross scratches.
brush=np.zeros((N,N))
for frequency in [47,89,143,199]:brush+=np.sin(2*np.pi*(frequency*y+2*x))*.25
steel=.93+.014*brush+.004*fine
save('BrushedSteel',steel,.000055*brush+.000008*fine,.30+.065*brush+.015*medium,.95)

# Clean one-metre industrial porcelain tile, recessed grout and gentle tile variation.
edge=np.minimum.reduce([x,1-x,y,1-y])
grout=np.clip((.010-edge)/.006,0,1)
floor=.93+.012*coarse+.009*medium+.004*fine-.22*grout
save('FactoryTile',floor,.000035*medium-.0014*grout,.36+.02*medium+.33*grout,0)

# Fine orange-peel powder coating. Neutral tint preserves the exact brand base colour.
save('PaintedMetal',.97+.006*medium+.003*fine,.000035*fine,.43+.02*medium,0)

# Moulded rubber: fine pores, no decorative or misleading tread pattern.
save('Rubber',.90+.018*medium+.01*fine,.00012*fine,.79+.025*medium,0)

# Long continuous wood fibres, periodically warped; neutral map tints from Wood material.
warp=.025*np.sin(2*np.pi*y)+.012*np.sin(2*np.pi*(2*y+x))+.002*coarse
grain=np.sin(2*np.pi*(58*(x+warp))+.16*medium)
veins=np.clip(grain,0,1)**12
wood=.94-.10*veins+.012*medium+.025*coarse
save('WoodGrain',wood,.000035*veins+.00001*medium,.64+.035*veins,0)

# Kraft fibre and subtle corrugation, without fictional printed labels.
fibres=.6*medium+.4*fine
card=.96+.012*fibres+.007*coarse
save('KraftCardboard',card,.00008*fibres+.000025*np.sin(2*np.pi*64*x),.85+.035*medium,0)

(OUT/'surfaces.json').write_text(json.dumps({'author':'Original project procedural textures','generated':'2026-10-24','size':N,'tileMetres':1,'normalConvention':'OpenGL tangent space; Unity TextureType.NormalMap','packedMap':'RGB metallic / A smoothness; linear','files':records},indent=2))
print('PBR_MAPS_CREATED',len(records))
