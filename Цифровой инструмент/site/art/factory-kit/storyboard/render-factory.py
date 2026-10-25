"""Editable factory overview for the gameplay study; does not alter Unity scenes."""
exec(open(str(__import__('pathlib').Path(__file__).with_name('render-scenes.py'))).read().split('# Compact laboratory')[0])
from bpy_extras.object_utils import world_to_camera_view
floor=box('Factory floor',(0,0,-.11),(18,13,.16),bpy.data.materials['Floor'])
for x in [-7,-3,1,5]:instance('Wall_Window_4m',(x,6,0))
for x in [-6,-3.5]:instance('Fermentation_Tank',(x,3.5,0))
instance('Control_Cabinet',(-1.5,4.4,0))
instance('Valve_Handwheel',(-2.4,2.6,1.05),scale=1.6)
for x in [2.5,4.6,6.7]:instance('Lab_Bench_2m',(x,4.3,0))
instance('PH_Meter',(3,4.1,.96),scale=1.6);instance('Test_Tube_Rack',(2,4.3,.96))
instance('Lab_Balance',(5,4.1,.96),scale=1.5);instance('Sample_Bottle',(5.6,4.1,.96),scale=2)
instance('Tablet',(6.8,4.1,.96),scale=1.6)
for x in [-3,1]:instance('Conveyor_4m',(x,.1,0),math.pi/2)
for x in [-4.5+i*.4 for i in range(20)]:instance('Sample_Bottle',(x,.1,1.0),scale=1.3)
instance('Filling_Machine',(3.7,.1,0));instance('Pallet_Loaded',(7,-3.3,0));instance('Pallet_Jack',(5.5,-3.4,0))
instance('Lab_Bench_2m',(-6,-3.7,0));instance('Tablet',(-6,-3.7,.96),scale=1.8)
instance('Lab_Stool',(-6,-4.5,0));instance('Locker',(-8,3.7,0))
for x,y,sx,sy in [(-4.8,1.8,6,.055),(-4.8,5.3,6,.055),(4.7,3.05,6,.055),(0,-1.2,9,.055),(6,-4.7,3,.055)]:box('Safety line',(x,y,.004),(sx,sy,.012),material('Safety yellow '+str(x)+str(y),(.95,.58,.07)))
text('ЛАБОРАТОРИЯ',(4.5,5.94,2.4),.33)
text('ОТБОР ПРОБ',(-4.6,5.94,2.4),.3)
text('РОЗЛИВ',(0,-.1,1.7),.21,rotation=(math.pi/2,0,0))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.world.color=(.65,.65,.65);scene.view_settings.view_transform='AgX'
for name,p,power,size in [('Daylight',(-3,1,12),2600,9),('Fill',(3,-6,8),1800,8)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;d.color=(1,.94,.84);o=bpy.data.objects.new(name,d);layout.objects.link(o);o.location=p;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Factory study camera');camera=bpy.data.objects.new('Factory study camera',d);layout.objects.link(camera);scene.camera=camera;camera.location=(0,-16,21);camera.rotation_euler=(Vector((0,.2,0))-camera.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=20
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
bpy.context.view_layer.update()
def proj(p):
 v=world_to_camera_view(scene,camera,Vector(p));return [v.x,1-v.y]
(OUT/'map.json').write_text(json.dumps({'origin':proj((0,0,0)),'x':proj((1,0,0)),'y':proj((0,1,0))},indent=2))
scene.render.filepath=str(OUT/'factory.png');bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/factory-kit/storyboard/factory-set.blend'))
# A small original blockout actor, rendered with the same viewing angle.
for o in layout.objects:
 if o.type not in ['LIGHT','CAMERA']:o.hide_render=True
coat=material('Actor white coat',(.91,.92,.91));skin=material('Actor skin',(.55,.30,.18));hair=material('Actor hair',(.07,.035,.018))
def ball(name,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=p);o=own(bpy.context.object,name,m);o.scale=s;return o
for x in [-.13,.13]:
 ball('Trouser',(x,0,.38),(.095,.10,.34),black);ball('Shoe',(x,-.055,.09),(.11,.18,.09),black)
ball('Lab coat',(0,0,.92),(.32,.19,.49),coat)
for x in [-.35,.35]:ball('Sleeve',(x,0,.96),(.095,.105,.30),coat);ball('Hand',(x,-.02,.68),(.075,.075,.09),skin)
ball('Head',(0,0,1.58),(.18,.17,.23),skin);ball('Hair',(0,.035,1.72),(.19,.17,.12),hair);ball('Bun',(0,.18,1.72),(.105,.1,.105),hair)
box('Red lanyard',(0,-.19,1.05),(.055,.02,.35),red);box('Badge',(.02,-.21,.94),(.13,.02,.11),paper)
camera.location=(0,-8,11);camera.rotation_euler=(Vector((0,0,.88))-camera.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=2.35
scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.film_transparent=True;scene.render.filepath=str(OUT/'player.png');bpy.ops.render.render(write_still=True)
