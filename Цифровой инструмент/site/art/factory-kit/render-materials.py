"""Close-up renders of actual source materials, for the offline asset catalog."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/factory-kit/assembly-preview.blend'))
bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/factory-kit/factory-kit.blend'))
for c in list(bpy.context.scene.collection.children):bpy.context.scene.collection.children.unlink(c)
collection=bpy.data.collections.new('Material closeups');bpy.context.scene.collection.children.link(collection)
def move(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    collection.objects.link(o)
def cube(name,position,size,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=position);o=bpy.context.object;move(o);o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    uv=o.data.uv_layers.active
    for f in o.data.polygons:
        axes=[0,1] if abs(f.normal.z)>.5 else ([0,2] if abs(f.normal.y)>.5 else [1,2])
        for li in f.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]+.5,co[axes[1]]+.5)
    o.data.materials.append(mat);b=o.modifiers.new('Edge radius','BEVEL');b.width=.012;b.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o
plate=cube('One metre surface',(0,0,.06),(1,1,.12),bpy.data.materials['Steel'])
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=.2,location=(.22,.18,.32));ball=bpy.context.object;move(ball)
for f in ball.data.polygons:f.use_smooth=True
background=bpy.data.materials.new('SampleBackground');background.diffuse_color=(.88,.87,.84,1)
cube('Background',(0,0,-.05),(200,200,.05),background)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.world.color=(.7,.7,.7);scene.view_settings.view_transform='AgX'
for name,p,power,size in [('Key',(-2,-2,4),700,3),('Rim',(2,1,3),500,2)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size;o=bpy.data.objects.new(name,data);collection.objects.link(o);o.location=p;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',d);collection.objects.link(camera);camera.location=(1.3,-1.8,1.8);camera.rotation_euler=(Vector((0,0,.12))-camera.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=1.6;scene.camera=camera
scene.render.resolution_x=600;scene.render.resolution_y=480;scene.render.resolution_percentage=100
output=ROOT/'docs/game/asset-library/materials';output.mkdir(exist_ok=True)
for surface,material in [('BrushedSteel','Steel'),('FactoryTile','Floor'),('PaintedMetal','Red'),('WoodGrain','Wood'),('KraftCardboard','Cardboard'),('Rubber','Rubber')]:
    m=bpy.data.materials[material];plate.data.materials[0]=m;ball.data.materials.clear();ball.data.materials.append(m)
    scene.render.filepath=str(output/(surface+'.png'));bpy.ops.render.render(write_still=True)
print('MATERIAL_CLOSEUPS_RENDERED',6)
