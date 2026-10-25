"""Original modular Ochakovo environment kit. Run with Blender 5 --background --python.
Coordinates: metres, Z up in Blender; exported FBX uses Y up, -Z forward.
No external model service, third-party mesh, or corporate logo is baked into these models.
"""
import bpy
import math
import json
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'OchakovoFactoryWorld/Assets/FactoryKit'
DOC = ROOT / 'docs/game/asset-library'
MODELS = OUT / 'Models'
MODELS.mkdir(parents=True, exist_ok=True)
DOC.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)

def material(name, color, metallic=0, roughness=.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

M = {
    'Steel': material('Steel', (.56,.62,.64), .72, .28),
    'SteelDark': material('SteelDark', (.20,.25,.27), .65, .34),
    'White': material('White', (.88,.87,.83), .05, .48),
    'Red': material('Red', (.665,.0,.032), .12, .32),
    'Rubber': material('Rubber', (.028,.033,.038), 0, .65),
    'Glass': material('Glass', (.48,.73,.75), .22, .22),
    'Screen': material('Screen', (.025,.13,.17), .2, .25),
    'ScreenLight': material('ScreenLight', (.30,.78,.76), .1, .3),
    'Amber': material('Amber', (.29,.085,.018), .12, .25),
    'Wood': material('Wood', (.48,.29,.12), 0, .66),
    'Cardboard': material('Cardboard', (.66,.46,.25), 0, .82),
    'SafetyYellow': material('SafetyYellow', (.95,.57,.035), .08, .4),
    'Green': material('Green', (.15,.31,.075), 0, .73),
    'Grape': material('Grape', (.14,.06,.19), 0, .48),
    'Floor': material('Floor', (.69,.67,.61), .12, .48),
}
SURFACES={'Steel':'BrushedSteel','SteelDark':'BrushedSteel','Floor':'FactoryTile',
          'White':'PaintedMetal','Red':'PaintedMetal','Rubber':'Rubber','Wood':'WoodGrain','Cardboard':'KraftCardboard'}
for name,surface in SURFACES.items():
    m=M[name];nodes=m.node_tree.nodes;links=m.node_tree.links
    p=nodes.get('Principled BSDF')
    def image_node(suffix,linear=False):
        path=OUT/'Textures/Surfaces'/(surface+'_'+suffix+'.png')
        image=bpy.data.images.load(str(path),check_existing=True)
        if linear:image.colorspace_settings.name='Non-Color'
        node=nodes.new('ShaderNodeTexImage');node.image=image
        return node
    albedo=image_node('Albedo');multiply=nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1;multiply.inputs[2].default_value=m.diffuse_color
    links.new(albedo.outputs['Color'],multiply.inputs[1]);links.new(multiply.outputs[0],p.inputs['Base Color'])
    rough=image_node('Roughness',True);links.new(rough.outputs['Color'],p.inputs['Roughness'])
    normal=image_node('Normal',True);n=nodes.new('ShaderNodeNormalMap');links.new(normal.outputs['Color'],n.inputs['Color']);links.new(n.outputs[0],p.inputs['Normal'])
current = None
assets = []

def own(o, name, mat):
    o.name = name
    for c in list(o.users_collection): c.objects.unlink(o)
    current.objects.link(o)
    if mat: o.data.materials.append(M[mat])
    return o

def box(name, p, s, mat='Steel', bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o = own(bpy.context.object, name, mat)
    o.dimensions = s
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Planar face UVs at one texture repeat per metre, including floors and walls.
    uv=o.data.uv_layers.active
    for face in o.data.polygons:
        axis=max(range(3),key=lambda i:abs(face.normal[i]))
        axes=[i for i in range(3) if i!=axis]
        for li in face.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(co[axes[0]]+p[axes[0]],co[axes[1]]+p[axes[1]])
    if bevel:
        b = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        b.width = min(bevel, min(s)*.22); b.segments = 2
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=b.name)
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def cyl(name, p, radius, depth, mat='Steel', vertices=24, top=None):
    if top is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=p)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=top, depth=depth, location=p)
    o = own(bpy.context.object, name, mat)
    # Cylindrical wrapping in physical metres; top/bottom use planar UVs.
    uv=o.data.uv_layers.active
    for face in o.data.polygons:
        if abs(face.normal.z)>.95:
            for li in face.loop_indices:
                co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co.x,co.y)
        else:
            values=[]
            for li in face.loop_indices:
                co=o.data.vertices[o.data.loops[li].vertex_index].co
                values.append((li,(math.atan2(co.y,co.x)/math.tau)%1,co.z))
            crossing=max(v[1] for v in values)-min(v[1] for v in values)>.5
            for li,u,v in values:uv.data[li].uv=((u+1 if crossing and u<.5 else u)*math.tau*radius,v)
    for f in o.data.polygons: f.use_smooth = len(f.vertices)==4
    return o

def sphere(name,p,s,mat='Steel'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=p)
    o=own(bpy.context.object,name,mat);o.scale=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for f in o.data.polygons: f.use_smooth=True
    return o

def rod(name,a,b,r=.035,mat='Steel',vertices=12):
    a,b=Vector(a),Vector(b)
    o=cyl(name,(a+b)/2,r,(b-a).length,mat,vertices)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o

def torus(name,p,major,minor,mat='Steel',rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=24,minor_segments=8,location=p,rotation=rotation)
    o=own(bpy.context.object,name,mat)
    for f in o.data.polygons: f.use_smooth=True
    return o

def socket(name,p):
    o=bpy.data.objects.new(name,None);current.objects.link(o);o.location=p;o.empty_display_size=.12
    return o

def start(name,category,label,reference,collision='box',grid=.5):
    global current
    current=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(current)
    assets.append(dict(id=name,category=category,label=label,reference=reference,collision=collision,grid=grid))

def legs(w,d,h,mat='Steel',z=0):
    for x in [-w/2,w/2]:
        for y in [-d/2,d/2]:
            rod('Leg',(x,y,z+.06),(x,y,z+h),.045,mat)
            cyl('AdjustableFoot',(x,y,z+.035),.075,.07,'Rubber',12)

def gauge(p):
    o=cyl('GaugeBody',p,.13,.065);o.rotation_euler[0]=math.pi/2
    o=cyl('GaugeDial',(p[0],p[1]-.038,p[2]),.11,.008,'White');o.rotation_euler[0]=math.pi/2
    rod('GaugeNeedle',(p[0],p[1]-.048,p[2]),(p[0]+.05,p[1]-.048,p[2]+.06),.008,'Red',6)

def wheel(p,r=.18):
    torus('ValveWheel',p,r,.023,'Red',(math.pi/2,0,0))
    for angle in [0,math.pi/2]:
        rod('WheelSpoke',(p[0]-r*math.cos(angle),p[1],p[2]-r*math.sin(angle)),(p[0]+r*math.cos(angle),p[1],p[2]+r*math.sin(angle)),.015,'Red')
    socket('Interaction_Valve',p)

def panel(p=(0,0,1.25),size=(.72,.24,1)):
    x,y,z=p; w,d,h=size
    box('Cabinet',p,size,'White')
    box('HMIFrame',(x,y-d/2-.02,z+.18),(w*.8,.035,h*.39),'Rubber',.01)
    box('HMIDisplay',(x,y-d/2-.045,z+.18),(w*.7,.01,h*.31),'Screen',.005)
    for j in range(3):
        box('DisplayReadout',(x-w*.22+j*w*.21,y-d/2-.053,z+.18),(w*.10,.004,h*.14),'ScreenLight',0)
    for j,m in enumerate(['Red','SafetyYellow','Green']):
        o=cyl('Button',(x+(j-1)*w*.22,y-d/2-.04,z-h*.23),.036,.025,m,12);o.rotation_euler[0]=math.pi/2
    socket('Interaction_HMI',(x,y-d/2-.15,z+.18))

# Building kit: floor and wall dimensions are exact multiples of the assembly grid.
for name,size in [('Floor_4x4',(4,4,.16)),('Floor_2x2',(2,2,.16))]:
    start(name,'Architecture','Пол — '+name.split('_')[1],'panorama')
    box('Slab',(0,0,-.08),size,'Floor',.01)
    for x in [-size[0]/2+.01,size[0]/2-.01]: box('Joint',(x,0,.002),(.012,size[1],.004),'SteelDark',0)
start('Wall_4m','Architecture','Стена 4 м','panorama')
box('Panel',(0,0,1.75),(4,.18,3.5),'White')
for z in [.15,1.1,2.15,3.35]: box('PanelSeam',(0,-.095,z),(4,.012,.018),'Steel',0)
start('Wall_Window_4m','Architecture','Стена с окном','panorama')
for p,s in [((0,0,.55),(4,.18,1.1)),((0,0,3.25),(4,.18,.5)),((-1.8,0,2.05),(.4,.18,1.9)),((1.8,0,2.05),(.4,.18,1.9))]:box('WallSection',p,s,'White')
box('Window',(0,0,2.05),(3.2,.035,1.9),'Glass',0)
for x in [-1.6,0,1.6]: box('Mullion',(x,-.04,2.05),(.06,.1,1.9))
start('Wall_Door_4m','Architecture','Стена с красной дверью','panorama')
for p,s in [((-1.3,0,1.75),(1.4,.18,3.5)),((1.3,0,1.75),(1.4,.18,3.5)),((0,0,2.95),(1.2,.18,1.1))]:box('WallSection',p,s,'White')
box('DoorLeaf',(0,-.02,1.2),(1.16,.09,2.4),'Red');box('DoorWindow',(0,-.075,1.75),(.65,.025,.6),'Glass')
rod('DoorHandle',(.39,-.12,1.05),(.39,-.12,1.28),.025)
start('Column_4m','Architecture','Колонна 4 м','panorama')
box('Column',(0,0,2),(.3,.3,4),'White');box('BasePlate',(0,0,.06),(.5,.5,.12),'Steel')
start('Roof_Truss_8m','Architecture','Ферма 8 м','panorama')
for z in [0,.7]: rod('Chord',(-4,0,z),(4,0,z),.045)
for i in range(8):rod('Diagonal',(-4+i,0,(i%2)*.7),(-3+i,0,((i+1)%2)*.7),.025)
start('Light_Batten_2m','Architecture','Линейный светильник','panorama','none')
box('Fixture',(0,0,.05),(2,.18,.1));box('Diffuser',(0,0,-.01),(1.9,.14,.025),'White')
start('Floor_Marking_2m','Architecture','Разметка прохода','panorama','none')
box('Paint',(0,0,.003),(.07,2,.006),'SafetyYellow',0)
start('Stairs_1_5m','Architecture','Лестница на платформу','panorama')
for i in range(8):box('Tread',(0,i*.25,.1+i*.1875),(1,.27,.09),'Steel')
for x in [-.5,.5]:
    rod('Stringer',(x,-.1,.03),(x,1.95,1.5),.045)
    rod('Handrail',(x,-.1,1),(x,1.95,2.5),.028)
    for y,z in [(0,.1),(1.75,1.41)]:rod('Post',(x,y,z),(x,y,z+1),.025)
start('Catwalk_2m','Architecture','Платформа 2 м','panorama')
box('Deck',(0,0,1.5),(2,1.2,.12))
for x in [-.9,.9]:
    for y in [-.5,.5]: rod('Support',(x,y,.04),(x,y,1.5),.045)
for y in [-.55,.55]:
    rod('Rail',(-1,y,2.5),(1,y,2.5),.028)
    for x in [-1,0,1]:rod('RailPost',(x,y,1.5),(x,y,2.5),.025)

# Brewing / process equipment. Shapes are artistic adaptations, not engineering drawings.
for name,r,h,kind in [('Brew_Kettle',1.15,2.25,'kettle'),('Fermentation_Tank',.8,3.3,'cone'),('Storage_Tank',1,2.7,'flat'),('Wine_Tank',.95,2.6,'wine'),('Grain_Silo',1.3,4.4,'silo')]:
    start(name,'Process',{'Brew_Kettle':'Варочная ёмкость','Fermentation_Tank':'Бродильная ёмкость','Storage_Tank':'Накопительная ёмкость','Wine_Tank':'Винная ёмкость','Grain_Silo':'Зерновой силос'}[name],'brewing-vats' if kind=='kettle' else ('branches' if kind in ['silo','wine'] else 'fermentation-tanks'))
    bottom=.55 if kind in ['cone','silo'] else .4
    cyl('VesselShell',(0,0,bottom+h/2),r,h)
    if kind=='kettle':
        cyl('ConicalRoof',(0,0,bottom+h+.26),r,.52,top=.19)
        cyl('VentStack',(0,0,bottom+h+.75),.17,.5)
        cyl('ManwayRim',(0,-.53,bottom+h+.33),.30,.12)
        cyl('ManwayLid',(0,-.53,bottom+h+.4),.265,.025,'SteelDark')
        rod('LidHandle',(-.12,-.53,bottom+h+.47),(.12,-.53,bottom+h+.47),.025)
    else:
        sphere('TopDome',(0,0,bottom+h),(r,r,.24))
        cyl('TopHatch',(0,0,bottom+h+.27),.23,.1)
    for z in [bottom+.08,bottom+h-.08]: torus('ShellBand',(0,0,z),r+.007,.025)
    if kind in ['cone','silo']:cyl('ConicalOutlet',(0,0,.38),.15,.65,top=r)
    legs(r*1.3,r*1.3,bottom+.12)
    rod('Outlet',(0,-r*.8,.45),(0,-r-.37,.45),.075)
    wheel((0,-r-.38,.62),.14)
    gauge((r*.55,-r*.88,1.3))
    socket('Socket_In',(0,0,bottom+h+.35));socket('Socket_Out',(0,-r-.4,.45));socket('Interaction_Sample',(0,-r-.45,1))

for length in [1,2,4]:
    start('Pipe_Straight_'+str(length)+'m','Pipes','Труба '+str(length)+' м','panorama','none')
    rod('Tube',(0,0,0),(length,0,0),.075)
    for x in [0,length]:
        o=cyl('Clamp',(x,0,0),.10,.04);o.rotation_euler[1]=math.pi/2
    socket('Socket_In',(0,0,0));socket('Socket_Out',(length,0,0))
start('Pipe_Elbow_90','Pipes','Отвод 90°','panorama','none')
pts=[(.5*math.sin(i*math.pi/24),.5*(1-math.cos(i*math.pi/24)),0) for i in range(13)]
for a,b in zip(pts,pts[1:]):rod('ElbowSegment',a,b,.075)
socket('Socket_In',pts[0]);socket('Socket_Out',pts[-1])
start('Pipe_Tee','Pipes','Тройник','panorama','none')
rod('Main',(-.5,0,0),(.5,0,0),.075);rod('Branch',(0,0,0),(0,.5,0),.075)
for n,p in [('In',(-.5,0,0)),('Out',(.5,0,0)),('Branch',(0,.5,0))]:socket('Socket_'+n,p)
start('Valve_Handwheel','Pipes','Ручной клапан','panorama','none')
rod('Pipe',(-.3,0,.18),(.3,0,.18),.075);cyl('ValveBody',(0,0,.2),.13,.2);rod('Stem',(0,0,.2),(0,0,.5),.025);wheel((0,-.02,.5))
start('Pressure_Gauge','Pipes','Манометр','machinery-video','none');gauge((0,0,.18));rod('Stem',(0,0,0),(0,0,.15),.025);socket('Interaction_Read',(0,-.1,.18))
start('Centrifugal_Pump','Process','Насос на раме','machinery-video')
box('Base',(0,0,.07),(1.3,.65,.14));o=cyl('Motor',(.2,0,.38),.23,.65,'SteelDark');o.rotation_euler[1]=math.pi/2
o=cyl('Pump',(-.35,0,.38),.27,.22);o.rotation_euler[1]=math.pi/2
rod('Intake',(-.65,0,.38),(-.45,0,.38),.075);rod('Outlet',(-.35,0,.5),(-.35,0,.85),.075)
socket('Socket_In',(-.65,0,.38));socket('Socket_Out',(-.35,0,.85))
start('Heat_Exchanger','Process','Пластинчатый теплообменник','machinery-video')
for x in [-.5,.5]:box('EndPlate',(x,0,.9),(.10,.65,1.4),'Red')
for i in range(15):box('Plate',(-.42+i*.06,0,.9),(.025,.56,1.25),'Steel',.008)
legs(.95,.55,.3)
for z in [.5,1.3]:rod('Connection',(-.65,-.26,z),(-.65,-.52,z),.07)
start('CIP_Skid','Process','Модуль моечной станции','fermentation-tanks')
box('Skid',(0,0,.08),(2,.9,.16));legs(1.8,.7,.3)
for x in [-.55,.55]:
    cyl('CIPVessel',(x,0,1.05),.37,1.55);sphere('Dome',(x,0,1.82),(.37,.37,.14));rod('Drain',(x,0,.3),(x,-.65,.3),.045);wheel((x,-.65,.5),.12)
socket('Socket_CIP_Return',(-.55,-.7,.3));socket('Socket_CIP_Supply',(.55,-.7,.3))
start('Control_Cabinet','Process','Шкаф управления','machinery-video');panel((0,0,1.15),(.9,.4,1.9));legs(.7,.3,.3)
start('Operator_Console','Process','Пульт оператора','machinery-video')
box('Pedestal',(0,0,.55),(.55,.4,1.1),'SteelDark');box('Base',(0,0,.04),(.8,.65,.08));panel((0,0,1.35),(1,.4,.7))

def conveyor(length=2,roller=False):
    legs(.64,length-.3,.9)
    box('Bed',(0,0,.9),(.8,length,.12))
    if roller:
        for i in range(int(length/.16)):
            o=cyl('Roller',(0,-length/2+.09+i*.16,.99),.055,.68);o.rotation_euler[1]=math.pi/2
    else:box('Belt',(0,0,.98),(.68,length,.035),'Rubber',.004)
    for x in [-.37,.37]:
        rod('GuardRail',(x,-length/2,1.18),(x,length/2,1.18),.025)
        for y in [-length/2+.15,length/2-.15]:rod('RailSupport',(x,y,.94),(x,y,1.18),.02)
    socket('Socket_In',(0,-length/2,.98));socket('Socket_Out',(0,length/2,.98))

for n,l,r in [('Conveyor_2m',2,False),('Conveyor_4m',4,False),('Roller_Conveyor_2m',2,True)]:
    start(n,'Bottling','Конвейер '+str(l)+' м'+(' роликовый' if r else ''),'bottling-video');conveyor(l,r)
start('Conveyor_Corner_90','Bottling','Угловой конвейер','bottling-video')
for i in range(9):
    a=(i+.5)*math.pi/18
    o=box('BeltSection',(math.cos(a),math.sin(a),.98),(.75,.18,.12),'Rubber',.01);o.rotation_euler[2]=a
for a in [0,math.pi/4,math.pi/2]:rod('Leg',(math.cos(a),math.sin(a),.05),(math.cos(a),math.sin(a),.94),.05)
socket('Socket_In',(1,0,.98));socket('Socket_Out',(0,1,.98))
for name,label in [('Filling_Machine','Защищённый модуль розлива'),('Labeling_Machine','Модуль этикетировки'),('Packing_Machine','Упаковочная станция')]:
    start(name,'Bottling',label,'bottling-video');conveyor(2)
    for x in [-.57,.57]:
        for y in [-.8,.8]:box('FramePost',(x,y,1.45),(.075,.075,2.4))
    box('Top',(0,0,2.65),(1.22,1.75,.14),'White')
    for x in [-.58,.58]:box('SafetyGuard',(x,0,1.9),(.025,1.55,1.25),'Glass',.003)
    box('ServiceBase',(0,0,.55),(1.1,1.55,.6),'White')
    if name=='Filling_Machine':
        for y in [-.5,-.25,0,.25,.5]:rod('FillHead',(0,y,2.35),(0,y,1.35),.035)
    elif name=='Labeling_Machine':
        for y in [-.4,.4]:cyl('LabelRoll',(.27,y,1.3),.19,.35,'White')
    else:box('PackingHead',(0,0,1.75),(.5,.7,.5),'Red')
    panel((.8,0,1.1),(.45,.3,.6));cyl('Beacon',(0,0,2.85),.075,.22,'Red',16)
    socket('Interaction_Inspect',(0,-1.15,1.3))

def bottle(p=(0,0,0)):
    x,y,z=p
    cyl('FilledPET',(x,y,z+.13),.045,.23,'Amber',16)
    cyl('Shoulder',(x,y,z+.267),.045,.045,'Amber',16,top=.018)
    cyl('Neck',(x,y,z+.306),.018,.035,'Amber',16)
    cyl('Cap',(x,y,z+.333),.023,.022,'Red',16)
    cyl('UnprintedLabelBand',(x,y,z+.15),.0458,.105,'Red',16)
start('PET_Bottle_Prototype','Props','Наполненная ПЭТ-бутылка без печати','product-reference','none',.05);bottle()
start('Can_Prototype','Props','Банка без печати','bottling-video','none',.05)
cyl('Can',(0,0,.085),.033,.16,'Red',24)
for z in [.008,.167]:cyl('Rim',(0,0,z),.034,.008)
torus('RingPull',(0,0,.173),.01,.002,'SteelDark')
start('Bottle_Tray_12','Props','Лоток с 12 бутылками','product-reference','none',.1)
box('Tray',(0,0,.025),(.36,.47,.05),'Cardboard')
for x in [-.12,0,.12]:
    for y in [-.18,-.06,.06,.18]:bottle((x,y,.05))

# Laboratory props use opaque tinted glass for predictable WebGL depth rendering.
start('Lab_Bench_2m','Laboratory','Лабораторный стол 2 м','chemist-video')
legs(1.8,.65,.88);box('Worktop',(0,0,.92),(2,.85,.08),'White')
box('DrawerUnit',(-.64,0,.45),(.62,.65,.8),'Red')
for z in [.23,.48,.73]:box('Handle',(-.64,-.35,z),(.26,.035,.025),'Steel')
box('Backsplash',(0,.4,1.08),(2,.035,.3),'White');socket('Socket_Worktop',(0,0,.96))
start('Lab_Stool','Laboratory','Табурет лаборатории','panorama')
cyl('Seat',(0,0,.6),.23,.08,'Red');rod('Stem',(0,0,.1),(0,0,.56),.045)
for a in range(5):rod('Foot',(0,0,.15),(.3*math.cos(a*math.tau/5),.3*math.sin(a*math.tau/5),.05),.025,'SteelDark')
start('Erlenmeyer_Flask','Laboratory','Колба с пробой','chemist-video','none',.05)
cyl('GlassBody',(0,0,.09),.075,.17,'Glass',24,top=.022);cyl('Neck',(0,0,.2),.022,.07,'Glass');cyl('Sample',(0,0,.05),.064,.08,'Amber',24,top=.045);torus('Rim',(0,0,.237),.023,.005)
socket('Interaction_Sample',(0,0,.1))
start('Beaker','Laboratory','Мерный стакан','chemist-video','none',.05)
cyl('GlassBody',(0,0,.075),.055,.15,'Glass');cyl('Liquid',(0,0,.04),.051,.075,'Amber');torus('Lip',(0,0,.15),.055,.004)
for z in [.03,.06,.09,.12]:box('Graduation',(.0,-.055,z),(.025,.003,.002),'White',0)
start('Test_Tube_Rack','Laboratory','Штатив с пробирками','chemist-video','none',.05)
for z in [.02,.1]:box('Rack',(0,0,z),(.32,.12,.018),'White',.005)
for x in [-.12,-.06,0,.06,.12]:cyl('Tube',(x,0,.105),.014,.16,'Glass',12);cyl('Cap',(x,0,.19),.017,.018,'Red',12)
start('Lab_Balance','Laboratory','Лабораторные весы','chemist-video','none',.05)
box('Instrument',(0,0,.04),(.3,.32,.08),'White');cyl('Pan',(0,.02,.09),.11,.025);box('Display',(0,-.14,.075),(.16,.03,.03),'Screen');socket('Interaction_Read',(0,-.18,.09))
start('Microscope','Laboratory','Микроскоп','chemist-video','none',.05)
box('Base',(0,0,.035),(.26,.32,.07),'White');rod('Arm',(0,.09,.07),(0,.09,.38),.045,'White');box('Stage',(0,0,.2),(.21,.18,.025),'Rubber')
rod('OpticalTube',(0,.08,.38),(0,-.04,.47),.035,'White');rod('Eyepiece',(0,-.04,.47),(0,-.08,.5),.027,'Rubber');rod('Objective',(0,.04,.36),(0,.04,.25),.023)
start('PH_Meter','Laboratory','Измеритель с электродом','chemist-video','none',.05)
box('Instrument',(0,0,.055),(.23,.26,.11),'White');box('Screen',(0,-.08,.112),(.14,.09,.008),'Screen');rod('ProbeStand',(.15,.08,0),(.15,.08,.4),.008);rod('Arm',(.15,.08,.4),(.05,.08,.4),.008);rod('Electrode',(.05,.08,.4),(.05,.08,.2),.008,'Rubber')
socket('Interaction_Read',(0,-.2,.12))
start('Sample_Bottle','Laboratory','Бутылка для пробы','chemist-video','none',.05)
cyl('Bottle',(0,0,.07),.035,.13,'Amber',16);cyl('Lid',(0,0,.145),.038,.025,'White',16);box('Label',(0,-.035,.08),(.045,.003,.05),'White',0)

# Logistics / shared set dressing.
def pallet():
    for x in [-.5,0,.5]:
        for y in [-.35,.35]:box('Block',(x,y,.09),(.15,.15,.12),'Wood',.01)
    for y in [-.4,-.2,0,.2,.4]:box('DeckBoard',(0,y,.17),(1.2,.15,.04),'Wood',.006)
    for x in [-.5,0,.5]:box('BottomRunner',(x,0,.025),(.15,.8,.05),'Wood',.006)
start('Euro_Pallet','Logistics','Поддон 1200×800','bottling-video',grid=.1);pallet()
start('Carton_Box','Logistics','Транспортная коробка','panorama',grid=.1)
box('Carton',(0,0,.2),(.6,.4,.4),'Cardboard',.012);box('Tape',(0,0,.402),(.055,.4,.005),'White',0)
start('Pallet_Loaded','Logistics','Поддон с коробками','bottling-video',grid=.1);pallet()
for z in [.39,.8,1.21]:
    for x in [-.3,.3]:
        for y in [-.2,.2]:box('Carton',(x,y,z),(.58,.38,.4),'Cardboard');box('Tape',(x,y,z+.202),(.045,.38,.005),'White',0)
start('Warehouse_Rack_3m','Logistics','Складской стеллаж 3 м','panorama')
for x in [-1.45,1.45]:
    for y in [-.5,.5]:box('Upright',(x,y,1.8),(.08,.08,3.6),'SteelDark')
for z in [.2,1.5,2.8]:
    box('Shelf',(0,0,z),(3,1.1,.08),'Steel')
    for y in [-.53,.53]:box('CrossBeam',(0,y,z-.07),(3,.08,.16),'Red')
start('Pallet_Jack','Logistics','Ручная тележка','panorama')
for x in [-.24,.24]:box('Fork',(x,.28,.10),(.16,1.2,.10),'Red');o=cyl('SmallWheel',(x,.7,.055),.055,.10,'Rubber',12);o.rotation_euler[1]=math.pi/2
box('HydraulicBody',(0,-.4,.22),(.55,.3,.35),'Red');rod('HandleStem',(0,-.43,.3),(0,-.68,1.1),.035,'SteelDark');torus('Handle',(0,-.68,1.17),.14,.025,'Rubber',(math.pi/2,0,0))
start('Safety_Bollard','Logistics','Защитный столбик','panorama')
cyl('Post',(0,0,.45),.09,.9,'SafetyYellow',16);cyl('Base',(0,0,.04),.16,.08,'SteelDark');cyl('Band',(0,0,.65),.092,.12,'Rubber',16)
start('Locker','Logistics','Шкаф для формы','chemist-video')
box('Body',(0,0,.95),(.8,.5,1.9),'White')
for x in [-.2,.2]:
    box('Door',(x,-.26,.97),(.38,.025,1.82),'Red')
    box('Handle',(x+.1,-.29,.95),(.025,.025,.15),'Steel')
    for z in [1.55,1.6,1.65]:box('Vent',(x,-.277,z),(.2,.004,.012),'SteelDark',0)
start('Tablet','Props','Рабочий планшет','panorama','none',.05)
box('Case',(0,0,.012),(.2,.28,.024),'Rubber',.014);box('Screen',(0,0,.026),(.174,.24,.005),'Screen',.006)
start('Clipboard','Props','Планшет с листом','panorama','none',.05)
box('Board',(0,0,.008),(.24,.33,.016),'Red',.008);box('Paper',(0,0,.018),(.21,.285,.002),'White',0);box('Clip',(0,.14,.026),(.08,.035,.014))
start('Grain_Sack','Agriculture','Мешок зерна','malt-house')
sphere('Sack',(0,0,.35),(.24,.17,.35),'Cardboard');cyl('TiedNeck',(0,0,.65),.07,.12,'Cardboard',12)
start('Malt_Hopper','Agriculture','Приёмный бункер','malt-house')
legs(1.4,1.4,1.8);box('UpperBin',(0,0,1.7),(1.6,1.6,1),'Steel');cyl('HopperCone',(0,0,.9),.15,.65,'Steel',4,top=1.1);cyl('Outlet',(0,0,.4),.15,.35)
start('Wine_Barrel','Agriculture','Дубовая бочка','branches')
for z,r in [(.1,.30),(.25,.35),(.5,.38),(.75,.35),(.9,.30)]:
    cyl('Staves',(0,0,z),r,.18,'Wood',24)
for z,r in [(.13,.315),(.3,.365),(.7,.365),(.87,.315)]:torus('Hoop',(0,0,z),r,.022,'SteelDark')
start('Vineyard_Row_4m','Agriculture','Секция виноградника 4 м','branches')
for x in [-2,0,2]:box('Post',(x,0,.9),(.08,.08,1.8),'Wood')
for z in [.65,1.2,1.65]:rod('TrellisWire',(-2,0,z),(2,0,z),.008)
for x in [-1.5,-.5,.5,1.5]:
    rod('Vine',(x,0,0),(x+.12,0,1.4),.035,'Wood')
    for dx in [-.2,.1,.35]:
        sphere('Foliage',(x+dx,0,1.3+dx*.4),(.3,.22,.24),'Green')
    for dz in [0,.06,.12]:sphere('GrapeCluster',(x,-.17,1.1-dz),(.055,.055,.07),'Grape')

# Consolidate fixed parts by material: small draw-call count, named sockets remain separate.
for a in assets:
    c=bpy.data.collections[a['id']]
    for mat in M:
        objs=[o for o in c.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name==mat]
        if not objs:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs:o.select_set(True)
        bpy.context.view_layer.objects.active=objs[0]
        bpy.ops.object.join(); o=bpy.context.object;o.name=a['id']+'_'+mat
        bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.select_all(action='DESELECT')
    for o in c.objects:o.select_set(True)
    f=MODELS/a['category']/(a['id']+'.fbx');f.parent.mkdir(exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=str(f),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False,use_mesh_modifiers=True)
    coords=[o.matrix_world@Vector(v) for o in c.objects if o.type=='MESH' for v in o.bound_box]
    lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
    a['size']=[round(hi[i]-lo[i],4) for i in [0,2,1]]
    a['triangles']=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in c.objects if o.type=='MESH')
    a['renderers']=sum(o.type=='MESH' for o in c.objects)
    a['sockets']=[o.name for o in c.objects if o.type=='EMPTY']
    a['path']='Models/'+a['category']+'/'+a['id']+'.fbx'
    a['surfaces']=sorted({SURFACES[o.data.materials[0].name] for o in c.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name in SURFACES})
    a['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
    a['license']='Original project geometry';a['status']='stylized concept; not a measured replica'

(OUT/'catalog.json').write_text(json.dumps({'version':1,'units':'metres','up':'Y in Unity','materialLibrary':{'textures':'Textures/Surfaces','sets':sorted(set(SURFACES.values())),'resolution':512,'maps':['Albedo','Normal','Roughness','MetallicSmoothness']},'assets':assets},ensure_ascii=False,indent=2))
(DOC/'catalog.json').write_text((OUT/'catalog.json').read_text())

# Source library, laid out on a grid. Geometry exports above remain at local origin.
for i,a in enumerate(assets):
    offset=Vector(((i%8)*5, (i//8)*6,0))
    for o in bpy.data.collections[a['id']].objects:o.location+=offset
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/factory-kit/factory-kit.blend'))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/factory-kit/factory-kit.blend'))

# Separate presentation arrangement assembled exclusively from the exported source kit.
for c in list(bpy.context.scene.collection.children):bpy.context.scene.collection.children.unlink(c)
current=bpy.data.collections.new('Presentation');bpy.context.scene.collection.children.link(current)
def instance(name,p=(0,0,0),angle=0):
    a=next(a for a in assets if a['id']==name);idx=assets.index(a)
    offset=Vector(((idx%8)*5,(idx//8)*6,0))
    root=bpy.data.objects.new(name,None);current.objects.link(root);root.location=p;root.rotation_euler[2]=angle
    for src in bpy.data.collections[name].objects:
        if src.type!='MESH':continue
        o=src.copy();current.objects.link(o);o.parent=root;o.location=src.location-offset
    return root
for x in [-6,-2,2,6]:
    for y in [-4,0,4]:instance('Floor_4x4',(x,y,0))
for x in [-6,-2,2,6]:instance('Wall_Window_4m',(x,6,0))
for y in [-4,0,4]:instance('Wall_4m',(-8,y,0),math.pi/2)
for x in [-6,-3.1]:instance('Brew_Kettle',(x,3.8,0))
instance('Fermentation_Tank',(-6,0,0));instance('CIP_Skid',(-3.3,.2,0));instance('Control_Cabinet',(-.9,4.9,0))
for y in [-2,0,2]:instance('Conveyor_2m',(1,y,0))
instance('Filling_Machine',(1,0,0));instance('Packing_Machine',(1,-3.5,0))
for y in [-2.5,-1.7,1.3,2.1]:instance('Bottle_Tray_12',(1,y,1))
for x in [3.7,6]:
    instance('Lab_Bench_2m',(x,4.6,0));instance('Lab_Stool',(x,3.5,0))
instance('Microscope',(3.1,4.5,.96));instance('PH_Meter',(4,4.5,.96));instance('Erlenmeyer_Flask',(5.5,4.3,.96));instance('Test_Tube_Rack',(6.1,4.6,.96));instance('Lab_Balance',(6.5,4.5,.96))
instance('Warehouse_Rack_3m',(5.3,-.3,0));instance('Pallet_Loaded',(5,-3.2,0));instance('Pallet_Jack',(6.4,-3.4,0));instance('Euro_Pallet',(4.8,-.3,.25))
for x in [-1.2,2.5]:instance('Floor_Marking_2m',(x,-3,0))
instance('Operator_Console',(-.4,-.4,0));instance('Catwalk_2m',(-4,5,0));instance('Safety_Bollard',(2.3,-4.8,0))
for x in [-6,-3.1]:
    instance('Pipe_Straight_2m',(x,4,3.8),math.pi/2)
box('StageGround',(0,0,-.23),(200,200,.2),'White',0)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.world.color=(.55,.55,.55)
scene.view_settings.view_transform='AgX'
def area(name,p,power,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);current.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Warm softbox',(0,-2,13),2300,10,(0,0,0));area('Window daylight',(3,8,7),1800,8,(0,0,0));area('Front fill',(8,-8,6),1000,8,(0,0,0))
d=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',d);current.objects.link(camera)
camera.location=(19,-25,24);camera.rotation_euler=(Vector((0,0,.5))-camera.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=25
scene.camera=camera;scene.render.resolution_x=1920;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(DOC/'factory-kit-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/factory-kit/assembly-preview.blend'))
bpy.ops.render.render(write_still=True)
print('FACTORY_KIT_EXPORTED',len(assets),'models',sum(a['triangles'] for a in assets),'triangles')
