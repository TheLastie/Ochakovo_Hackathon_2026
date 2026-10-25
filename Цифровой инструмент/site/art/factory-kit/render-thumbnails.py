"""Render true mesh thumbnails, not concept art. Run after generate.py."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/factory-kit/factory-kit.blend'))
catalog=json.loads((ROOT/'docs/game/asset-library/catalog.json').read_text())['assets']
output=ROOT/'docs/game/asset-library/thumbnails';output.mkdir(exist_ok=True)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
scene.render.resolution_x=400;scene.render.resolution_y=320;scene.render.resolution_percentage=100
scene.world.color=(.6,.6,.6);scene.view_settings.view_transform='AgX'
rig=bpy.data.collections.new('Thumbnail rig');scene.collection.children.link(rig)
d=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',d);rig.objects.link(camera);d.type='ORTHO';scene.camera=camera
for name,p,power,size in [('Key',(4,-5,8),1100,6),('Fill',(-4,2,5),800,5)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size
    o=bpy.data.objects.new(name,data);rig.objects.link(o);o.location=p
    o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
for collection in scene.collection.children:collection.hide_render=True
rig.hide_render=False
for i,a in enumerate(catalog):
    c=bpy.data.collections[a['id']];c.hide_render=False
    offset=Vector(((i%8)*5,(i//8)*6,0))
    for o in c.objects:o.location-=offset
    coords=[o.matrix_world@Vector(v) for o in c.objects if o.type=='MESH' for v in o.bound_box]
    # Re-evaluate transforms after moving the grid collection back to local origin.
    bpy.context.view_layer.update()
    coords=[o.matrix_world@Vector(v) for o in c.objects if o.type=='MESH' for v in o.bound_box]
    low=Vector([min(p[j] for p in coords) for j in range(3)]);high=Vector([max(p[j] for p in coords) for j in range(3)])
    center=(low+high)/2;size=max((high-low).length,.1)
    camera.location=center+Vector((1.2,-1.8,1.3))*size
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=size*1.1;d.clip_start=.001
    for o in rig.objects:
        if o.type=='LIGHT':o.location=center+Vector((3 if o.name=='Key' else -3,-4 if o.name=='Key' else 2,6))*max(size,.5);o.data.energy=(1100 if o.name=='Key' else 800)*max(size,.5)**2;o.data.size=5*max(size,.5);o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(output/(a['id']+'.png'));bpy.ops.render.render(write_still=True)
    c.hide_render=True
print('THUMBNAILS_RENDERED',len(catalog))
