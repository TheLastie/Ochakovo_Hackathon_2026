"""Quaternius CC0 base meshes + own workwear, rig-bound garments and motion assembly.
Run in Blender 5.0. Saves editable .blend and game FBX; never touches Unity scene.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'OchakovoFactoryWorld/Assets/FactoryWorld/Characters';VENDOR=ROOT/'art/characters/vendor';ART=ROOT/'art/characters';PREVIEW=ROOT/'docs/game/location/characters';PREVIEW.mkdir(exist_ok=True,parents=True)
rig=None

def mat(name,color,texture=None,rough=.7):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(OUT/'Textures'/texture),check_existing=True);mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*color,1);m.node_tree.links.new(t.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],p.inputs['Base Color'])
 else:
  # Woven surface, packed in the editable source; Unity uses the matching cloth material.
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=230;n.inputs['Detail'].default_value=1;b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.002;m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 return m

def skin_bind(o,bone):
 if bone not in o.vertex_groups:o.vertex_groups.new(name=bone)
 o.vertex_groups[bone].add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=rig;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);mod=o.modifiers.new('Rig deformation','ARMATURE');mod.object=rig

def cube(name,p,s,m,bone):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bev=o.modifiers.new('Rounded garment edge','BEVEL');bev.width=.005;bev.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bev.name)
 # Bake all mesh positions to armature local coordinates before binding.
 for v in o.data.vertices:v.co=o.matrix_world@v.co
 o.location=(0,0,0);skin_bind(o,bone);o.data.materials.append(m);return o

def ellipsoid(name,p,s,m,bone):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=p);o=bpy.context.object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for v in o.data.vertices:v.co=o.matrix_world@v.co
 o.location=(0,0,0);skin_bind(o,bone);o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o

def garment(body,name,predicate,m,offset=.02):
 o=body.copy();o.data=body.data.copy();bpy.context.collection.objects.link(o);o.name=name;o.data.materials.clear();o.data.materials.append(m)
 for mod in list(o.modifiers):
  if mod.type!='ARMATURE':o.modifiers.remove(mod)
 bm=bmesh.new();bm.from_mesh(o.data);drop=[f for f in bm.faces if not predicate(f.calc_center_median())];bmesh.ops.delete(bm,geom=drop,context='FACES');bm.normal_update()
 for v in bm.verts:v.co+=v.normal*offset
 bm.to_mesh(o.data);bm.free()
 # Smooth the skin's muscle relief into cloth; retain inherited vertex weights.
 smooth=o.modifiers.new('Cloth relax','SMOOTH');smooth.factor=.65;smooth.iterations=0 if name=='Red shoulder yoke' else 5;bpy.context.view_layer.objects.active=o
 # Apply before deformation so the authoring pose remains fixed.
 
 while o.modifiers.find(smooth.name)>0:bpy.ops.object.modifier_move_up(modifier=smooth.name)
 bpy.ops.object.modifier_apply(modifier=smooth.name)
 sol=o.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.006
 for f in o.data.polygons:f.use_smooth=True
 return o

def skirt(name,m):
 verts=[];faces=[];n=40
 for z,rx,ry in [(1.09,.17,.12),(.97,.25,.205),(.80,.30,.24),(.68,.315,.25)]:
  for i in range(n):a=i*math.tau/n;verts.append((math.cos(a)*rx,math.sin(a)*ry+(.03 if z>1.05 else -.015),z))
 for j in range(3):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(m);skin_bind(o,'pelvis')
 for f in mesh.polygons:f.use_smooth=True
 for side in ['l','r']:o.vertex_groups.new(name='thigh_'+side)
 for v in mesh.vertices:
  t=max(0,(.95-v.co.z)/.27)*.4
  if t>0:o.vertex_groups['pelvis'].add([v.index],1-t,'REPLACE');o.vertex_groups['thigh_'+('l' if v.co.x>0 else 'r')].add([v.index],t,'REPLACE')
 sol=o.modifiers.new('Coat hem thickness','SOLIDIFY');sol.thickness=.006
 return o

def normalize_mesh(o,arm):
 mx=arm.matrix_world.inverted()@o.matrix_world
 for v in o.data.vertices:v.co=mx@v.co
 o.parent=arm;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)

def setup(role,sex,lab):
 global rig
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 bpy.ops.import_scene.fbx(filepath=str(VENDOR/(sex+'_Base.fbx')))
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.name='FactoryRig';meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in meshes:normalize_mesh(o,rig)
 rig.rotation_euler=(0,0,0);rig.location=(0,0,0);body=max(meshes,key=lambda o:len(o.data.vertices))
 factor=1.775/max(v.co.z for v in body.data.vertices)
 for o in meshes:
  for v in o.data.vertices:v.co*=factor
 bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 for bone in rig.data.edit_bones:bone.head*=factor;bone.tail*=factor
 bpy.ops.object.mode_set(mode='OBJECT')
 for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)

 # Source faces look towards -Y in armature space.
 tex='T_Superhero_Female_Light_BaseColor.png' if sex=='Female' else 'T_Superhero_Male_Ligh.png'
 skin=mat('Skin_'+sex,(1,1,1),tex,.72);eyes=mat('Eyes',(1,1,1),'T_Eye_Brown.png',.35);hair=mat('Hair',(.16,.075,.035),'T_Hair_2_BaseColor.png',.82)
 for o in meshes:
  for i,original in enumerate(list(o.data.materials)):o.data.materials[i]=skin if o==body else eyes if original and 'Eye' in original.name else hair
 white=mat('Coat fabric',(.87,.89,.88));navy=mat('Work fabric',(.075,.10,.14));red=mat('Red fabric',(.67,.007,.04));black=mat('Boot rubber',(.025,.028,.035));silver=mat('Reflective fabric',(.66,.7,.71));badge=mat('Badge paper',(.92,.92,.86));glove=mat('Nitrile gloves',(.2,.42,.52));
 shirt=garment(body,'Tailored coat' if lab else 'Work jacket',lambda p:.94<p.z<(1.50 if abs(p.x)<.14 else 1.62) and abs(p.x)<.66,white if lab else navy,.027)
 garment(body,'Work trousers',lambda p:.14<p.z<.98,navy,.025)
 garment(body,'Safety footwear',lambda p:p.z<.18,black,.018)
 # Remove hidden anatomy, leaving face/neck and actual articulated hands.
 bm=bmesh.new();bm.from_mesh(body.data);drop=[f for f in bm.faces if (f.calc_center_median().z<(1.50 if abs(f.calc_center_median().x)<.14 else 1.62) and abs(f.calc_center_median().x)<.64) or f.calc_center_median().z<1.0];bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(body.data);bm.free()
 if lab:
  skirt('Lab coat skirt',white)
  for x in [-.105,.105]:
   o=None
   cube('Patch pocket',(x,-.19,1.03),(.105,.008,.125),white,'spine_01')
  for z in [1.31,1.2,1.08,.96,.84]:ellipsoid('Coat button',(0,-.174,z),(.009,.004,.009),silver,'spine_02' if z>1.15 else 'pelvis')
  garment(next(o for o in meshes if o.name.startswith('Eyes')),'Unused',lambda p:False,white,0) if False else None
 else:
  shirt.data.materials.append(red)
  for poly in shirt.data.polygons:
   if poly.center.z>1.36 or abs(poly.center.x)>.25:poly.material_index=len(shirt.data.materials)-1
  cube('Jacket zip',(0,-.175,1.19),(.012,.012,.46),silver,'spine_02')
  for x in [-.105,.105]:cube('Chest pocket',(x,-.173,1.28),(.11,.015,.12),navy,'spine_03');cube('Reflective chest tape',(x,-.19,1.19),(.13,.01,.025),silver,'spine_02')
 cube('Employee badge',(.115,-.194,1.36),(.085,.012,.105),badge,'spine_03');cube('Badge stripe',(.115,-.202,1.382),(.075,.002,.017),red,'spine_03')
 # Curated CC0 hair is bound to the existing head bone.
 old=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(VENDOR/('Hair_Buns.fbx' if lab else 'Hair_SimpleParted.fbx')))
 for o in set(bpy.context.scene.objects)-old:
  if o.type=='MESH':
   if not lab:
    bpy.data.objects.remove(o,do_unlink=True);continue
   for v in o.data.vertices:v.co=o.matrix_world@v.co
   o.matrix_world=Matrix.Identity(4);o.data.materials.clear();o.data.materials.append(hair);skin_bind(o,'Head')
  elif o.type=='EMPTY':bpy.data.objects.remove(o,do_unlink=True)
 if not lab:
  ellipsoid('Work cap',(0,.01,1.75),(.118,.104,.065),red,'Head');cube('Cap peak',(0,-.10,1.715),(.22,.16,.025),red,'Head')
 # A rounded collar finishes the mesh's cut neckline.
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,major_radius=.093,minor_radius=.012,location=(0,.02,1.495));collar=bpy.context.object;collar.name='Finished garment collar'
 for v in collar.data.vertices:v.co=collar.matrix_world@v.co
 collar.location=(0,0,0);skin_bind(collar,'spine_03');collar.data.materials.append(white if lab else navy)
 # Rounded safety shoes cover the source barefoot toe silhouette.
 for side in ['l','r']:
  x=arm_x=rig.data.bones['foot_'+side].head_local.x
  ellipsoid('Safety boot toe',(x,-.09,.09),(.075,.15,.055),black,'foot_'+side)
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=1,depth=.03,location=(x,-.08,.025));sole=bpy.context.object;sole.name='Rounded safety sole';sole.scale=(.078,.155,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for v in sole.data.vertices:v.co=sole.matrix_world@v.co
  sole.location=(0,0,0);skin_bind(sole,'foot_'+side);sole.data.materials.append(black)
 rig.rotation_euler=(0,0,0)
 # Record texture bindings for Unity's Built-in materials.
 return rig

def animations(arm):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(VENDOR/'UAL1_Standard.fbx'))
 source=next(o for o in set(bpy.context.scene.objects)-before if o.type=='ARMATURE');source.rotation_euler=(0,0,0);source.location=(0,0,0)
 arm.animation_data_create();keep={};initial_rotation=arm.rotation_euler.copy();arm.rotation_euler=(0,0,0)
 sources=list(bpy.data.actions)
 for suffix,name in [('Idle_Loop','Idle'),('Walk_Loop','Walk'),('Idle_Torch_Loop','InspectSample'),('Interact','OperatePanel'),('Push_Loop','OperateValve')]:
  original=next(a for a in sources if a.name.endswith('|'+suffix));source.animation_data.action=original;source.animation_data.action_slot=original.slots[0]
  action=bpy.data.actions.new(name);action.use_fake_user=True;arm.animation_data.action=action
  start,end=map(int,original.frame_range)
  for frame in list(range(start,end+1,2))+([end] if (end-start)%2 else []):
   bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();desired={};root_delta=source.pose.bones['root'].matrix@source.data.bones['root'].matrix_local.inverted();orientation=root_delta.inverted()
   for bone in arm.data.bones:
    src=source.pose.bones.get(bone.name)
    rotated=(orientation@src.matrix@src.bone.matrix_local.inverted()@bone.matrix_local).to_quaternion() if src else bone.matrix_local.to_quaternion()
    if bone.parent:
     offset=bone.parent.matrix_local.inverted()@bone.head_local
     position=desired[bone.parent.name]@offset
     if bone.name=='pelvis' and src:
      bob=(orientation@src.matrix).translation.z-src.bone.head_local.z
      position.z+=bob
    else:position=bone.head_local.copy();rotated=bone.matrix_local.to_quaternion()
    desired[bone.name]=Matrix.LocRotScale(position,rotated,Vector((1,1,1)))
   for bone in arm.data.bones:
    if bone.parent:
     rest=bone.parent.matrix_local.inverted()@bone.matrix_local;basis=rest.inverted()@desired[bone.parent.name].inverted()@desired[bone.name]
    else:basis=bone.matrix_local.inverted()@desired[bone.name]
    pb=arm.pose.bones[bone.name];pb.rotation_mode='QUATERNION';pb.matrix_basis=basis
    for path in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data_path=path,frame=frame,group=bone.name)
  keep[name]=action
 for o in set(bpy.context.scene.objects)-before:bpy.data.objects.remove(o,do_unlink=True)
 for a in list(bpy.data.actions):
  if a not in keep.values():bpy.data.actions.remove(a)
 arm.rotation_euler=initial_rotation;arm.animation_data.action=keep['Idle'];arm.animation_data.action_slot=keep['Idle'].slots[0]
 return keep

def render(arm,role,actions):
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.world=bpy.data.worlds.new('Studio world');scene.world.color=(.4,.4,.4);scene.render.resolution_x=900;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
 floor=mat('Studio floor',(.78,.76,.70));bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.01));bpy.context.object.data.materials.append(floor);bpy.context.object.name='PreviewFloor'
 for p,power,size in [((3,-4,5),500,4),((-3,-1,3),350,3),((0,4,4),500,3)]:
  d=bpy.data.lights.new('Softbox','AREA');d.energy=power;d.size=size;o=bpy.data.objects.new('Softbox',d);bpy.context.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
 d=bpy.data.cameras.new('PreviewCamera');cam=bpy.data.objects.new('PreviewCamera',d);bpy.context.collection.objects.link(cam);cam.location=(2.8,-5,2.6);cam.rotation_euler=(Vector((0,0,.95))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=2.2;scene.camera=cam
 for state,frame in [('Idle',20),('Walk',10),('InspectSample' if role=='chemist' else 'OperatePanel',20)]:
  arm.animation_data.action=actions[state];arm.animation_data.action_slot=actions[state].slots[0];scene.frame_set(frame);scene.render.filepath=str(PREVIEW/f'{role}-{state}.png');bpy.ops.render.render(write_still=True)
 # Preview objects are excluded from the game export; kept in the editable source.

report=[]
for role,sex,lab in [('chemist','Female',True),('bottling','Male',False)]:
 if __import__('os').environ.get('CHARACTER_ROLE') and role!=__import__('os').environ['CHARACTER_ROLE']:continue
 arm=setup(role,sex,lab);actions=animations(arm);bpy.context.scene.render.fps=30
 # Export only the character meshes and armature, using baked motion clips.
 bpy.ops.object.select_all(action='DESELECT');arm.select_set(True)
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.context.view_layer.objects.active=arm
 if not __import__('os').environ.get('SKIP_EXPORT'):bpy.ops.export_scene.fbx(filepath=str(OUT/'Models'/f'{role}.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=.2,path_mode='STRIP',embed_textures=False)
 report.append({'role':role,'base':sex,'clips':list(actions),'vertices':sum(len(o.data.vertices) for o in bpy.context.scene.objects if o.type=='MESH')})
 
 if not __import__('os').environ.get('SKIP_PREVIEW'):render(arm,role,actions)
 bpy.data.orphans_purge(do_recursive=True)
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 for im in list(bpy.data.images):
  if im.users==0:bpy.data.images.remove(im)
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ART/f'{role}.blend'))
(ART/'manifest.json').write_text(json.dumps(report,indent=2));print('FACTORY_CHARACTERS_READY')
