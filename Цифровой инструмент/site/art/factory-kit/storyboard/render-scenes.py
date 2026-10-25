"""Render lab storyboard sets from editable project meshes, without changing Unity.
Blender 5.0, native source geometry and project surface textures.
"""
from pathlib import Path
import bpy,json,math
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/game/gameplay/chemist-storyboard/backgrounds';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/factory-kit/factory-kit.blend'))
bpy.context.preferences.filepaths.save_version=0
entries=json.loads((ROOT/'docs/game/asset-library/catalog.json').read_text())['assets']
for c in list(bpy.context.scene.collection.children):bpy.context.scene.collection.children.unlink(c)
layout=bpy.data.collections.new('Laboratory set');bpy.context.scene.collection.children.link(layout)

def instance(name,p=(0,0,0),angle=0,scale=1):
    idx=next(i for i,a in enumerate(entries) if a['id']==name)
    offset=Vector(((idx%8)*5,(idx//8)*6,0))
    root=bpy.data.objects.new(name,None);layout.objects.link(root);root.location=p;root.rotation_euler[2]=angle;root.scale=(scale,)*3
    for src in bpy.data.collections[name].objects:
        if src.type!='MESH':continue
        o=src.copy();layout.objects.link(o);o.parent=root;o.location=src.location-offset
    return root

def material(name,color,metal=0,rough=.5):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
black=material('Set ink',(.02,.025,.028));paper=material('Set paper',(.93,.92,.87));red=material('Set red',(.665,0,.032));amber=material('Set sample',(.18,.055,.009),.1,.2)
def own(o,name,mat):
    for c in list(o.users_collection):c.objects.unlink(o)
    layout.objects.link(o);o.name=name;o.data.materials.append(mat);return o
def box(name,p,s,mat=paper):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=own(bpy.context.object,name,mat);o.dimensions=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=o.modifiers.new('Soft corners','BEVEL');mod.width=.006;mod.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o
font_path=ROOT/'tmp/defense-build/ProximaNova-Bold.ttf'
font=bpy.data.fonts.load(str(font_path)) if font_path.exists() else None
def text(value,p,size=.03,rotation=(math.pi/2,0,0),mat=black):
    d=bpy.data.curves.new('Printed label','FONT');d.body=value;d.size=size;d.align_x='CENTER';d.align_y='CENTER'
    if font:d.font=font
    o=bpy.data.objects.new(value,d);layout.objects.link(o);o.location=p;o.rotation_euler=rotation;d.materials.append(mat);return o

# Compact laboratory, three distinct working places and a view into the factory.
for x in [-3,-1,1,3]:
    for y in [-2,0,2]:instance('Floor_2x2',(x,y,0))
for x in [-2,2]:instance('Wall_Window_4m',(x,3,0))
instance('Wall_Door_4m',(-4,1,0),math.pi/2)
instance('Lab_Bench_2m',(-2.15,1.9,0));instance('Lab_Bench_2m',(-.05,1.9,0));instance('Lab_Bench_2m',(2.05,1.9,0))
instance('Lab_Stool',(-2.5,.65,0));instance('Lab_Stool',(.4,.6,0));instance('Lab_Stool',(2.55,.65,0))
instance('Locker',(-3.65,-1.7,0),-math.pi/2)
instance('Control_Cabinet',(3.1,4.1,0));instance('Storage_Tank',(-2.1,5,0));instance('Fermentation_Tank',(.8,5.4,0))
instance('Test_Tube_Rack',(-1.47,2.05,.96));instance('Erlenmeyer_Flask',(-2.85,2.06,.96))
instance('PH_Meter',(-.15,1.7,.96),scale=1.5);instance('Beaker',(.18,1.68,.96),scale=1.5)
instance('Lab_Balance',(1.78,1.75,.96),scale=1.5);instance('Clipboard',(2.55,1.65,.96))
instance('Tablet',(2.65,2.08,.96));instance('Sample_Bottle',(.65,2.04,.96))

# Sample tray and large, genuinely printed identification tags.
box('Clean sampling tray',(-2.15,1.67,.985),(1.08,.40,.035),bpy.data.materials['Steel'])
for i,(id,subtitle) in enumerate([('К-240','Л-2'),('К-241','Л-2'),('—','Л-2')]):
    x=-2.5+i*.35
    instance('Sample_Bottle',(x,1.65,1.01),scale=1.55)
    box('Identification label',(x,1.594,1.135),(.095,.002,.10))
    text(id,(x,1.5915,1.15),.025);text(subtitle,(x,1.5915,1.115),.018)
    # A physical card on the tray supports selection without floating fantasy labels.
    box('Sample record',(x,1.42,1.009),(.25,.14,.004))
    text(id,(x,1.41,1.012),.035,rotation=(0,0,0))

# Prepared weighing dish (a storytelling prop, not an engineering vessel).
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.075,depth=.012,location=(1.77,1.75,1.12));own(bpy.context.object,'Weighing dish',bpy.data.materials['Steel'])
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.063,depth=.004,location=(1.77,1.75,1.128));own(bpy.context.object,'Prepared dry residue',amber)

# Small contextual product, using the existing authentic textured product mesh.
with bpy.data.libraries.load(str(ROOT/'art/factory-kit/products/products.blend'),link=False) as (source,target):
    target.collections=['Ochakovsky_Kvass_PET_500ml']
product=bpy.data.objects.new('Finished product context',None);layout.objects.link(product);product.location=(2.85,2.0,.96)
for c in target.collections:
    for src in list(c.objects):
        if src.type=='MESH':
            o=src.copy();layout.objects.link(o);o.parent=product

# Genuine company sign, kept out of generated text.
logo_mat=material('Original logo sign',(1,1,1),0,.7)
nodes=logo_mat.node_tree.nodes;p=nodes.get('Principled BSDF');image=nodes.new('ShaderNodeTexImage')
image.image=bpy.data.images.load(str(ROOT/'OchakovoFactoryWorld/Assets/FactoryKit/Textures/Ochakovo_Official.png'))
logo_mat.node_tree.links.new(image.outputs['Color'],p.inputs['Base Color']);logo_mat.node_tree.links.new(image.outputs['Alpha'],p.inputs['Alpha'])
box('Sign backing',(-.1,2.82,2.8),(1.75,.04,.48))
bpy.ops.mesh.primitive_plane_add(size=1,location=(-.1,2.793,2.8),rotation=(math.pi/2,0,0));o=own(bpy.context.object,'Genuine Ochakovo logo',logo_mat);o.scale=(1.55,.368,1)

# Warm daylight, soft contact shadows, readable metal surfaces.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.world.color=(.5,.5,.5);scene.view_settings.view_transform='AgX'
for name,p,power,size,target in [('Daylight',(0,1,6),1000,5,(0,1,0)),('Window',(0,5,3),700,5,(0,0,1)),('Soft front',(0,-4,4),500,5,(0,1,1))]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);layout.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Storyboard camera');camera=bpy.data.objects.new('Storyboard camera',d);layout.objects.link(camera)
scene.camera=camera;d.type='ORTHO';d.clip_start=.01;d.clip_end=100
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
views=[
    ('overview',(7.2,-9,7.4),(-.35,.8,.9),9.7),
    ('samples',(-1.65,-.2,2.4),(-2.15,1.65,1.08),1.75),
    ('instrument',(.55,-.6,2.15),(-.05,1.72,1.1),1.55),
    ('balance',(2.15,-.25,2.2),(1.8,1.75,1.05),1.65),
    ('journal',(3.2,-.3,2.5),(2.45,1.8,1.02),1.65),
]
for name,position,target,scale in views:
    camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    print('STORYBOARD_VIEW_RENDERED',name)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/factory-kit/storyboard/laboratory-set.blend'))
print('LABORATORY_STORYBOARD_READY')
