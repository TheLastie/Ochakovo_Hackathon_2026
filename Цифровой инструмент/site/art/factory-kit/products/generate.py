"""Original product meshes, LODs and genuine packaging textures. Blender 5.0."""
from pathlib import Path
import bpy,math,json,hashlib
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'OchakovoFactoryWorld/Assets/FactoryKit/Products'
DOC=ROOT/'docs/game/asset-library'
MODELS=OUT/'Models';MODELS.mkdir(parents=True,exist_ok=True)
(MODELS/'LOD1').mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)

def material(name,color,metallic=0,smoothness=.5,texture=None):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=1-smoothness
    if texture:
        node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(OUT/'Textures'/(texture+'_Albedo.png')),check_existing=True)
        m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    return m
specs=[
    dict(name='Product_PET_Kvass',color=[.012,.0028,.0006],metallic=0,smoothness=.76),
    dict(name='Product_PET_Headspace',color=[.15,.04,.003],metallic=0,smoothness=.78),
    dict(name='Product_Cap_Brown',color=[.035,.012,.002],metallic=0,smoothness=.34),
    dict(name='Product_Aluminium',color=[.68,.71,.72],metallic=.88,smoothness=.72),
    dict(name='Product_Lid_Inset',color=[.32,.36,.37],metallic=.82,smoothness=.55),
    dict(name='Product_Ochakovsky_Label',color=[1,1,1],metallic=0,smoothness=.48,texture='Ochakovsky_Label'),
    dict(name='Product_Mojito_Label',color=[1,1,1],metallic=.12,smoothness=.62,texture='Mojito_Label'),
]
M={s['name']:material(**s) for s in specs}
current=None
def link(o,name,mat):
    o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    current.objects.link(o)
    if mat:o.data.materials.append(M[mat])
    return o

def lathe(name,profile,segments,mat,lobe=0,ribs=0):
    verts=[]
    for z,r in profile:
        for i in range(segments+1):
            t=(i/segments-.5)*math.tau
            radius=r+lobe*math.cos(t*5)*max(0,1-z/.025)
            if ribs:radius+=ribs*(.5+.5*math.cos(t*(48 if segments>=48 else 12)))
            verts.append((radius*math.sin(t),-radius*math.cos(t),z))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*(segments+1)+i;faces.append((a,a+1,a+segments+2,a+segments+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);current.objects.link(o);mesh.materials.append(M[mat])
    uv=mesh.uv_layers.new(name='PackagingUV')
    z0,z1=profile[0][0],profile[-1][0]
    for face in mesh.polygons:
        face.use_smooth=True
        for li in face.loop_indices:
            vi=mesh.loops[li].vertex_index;ring=vi//(segments+1);u=(vi%(segments+1))/segments
            uv.data[li].uv=(u,(profile[ring][0]-z0)/max(z1-z0,.0001))
    return o

def cylinder(name,r,depth,z,mat,segments=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=depth,location=(0,0,z))
    o=link(bpy.context.object,name,mat)
    for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
    return o

def torus(name,p,major,minor,mat,segments=64,scale=(1,1,1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=segments,minor_segments=8,location=p)
    o=link(bpy.context.object,name,mat);o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for f in o.data.polygons:f.use_smooth=True
    return o

def socket(name,p):
    o=bpy.data.objects.new(name,None);current.objects.link(o);o.location=p;o.empty_display_size=.01

def kvass(segments,lod):
    p=[(0,.022),(.003,.028),(.008,.032),(.016,.033),(.024,.0335),(.031,.0325),(.039,.030),(.045,.0288),
       (.05,.0283),(.052,.0292),(.054,.028),(.062,.0273),(.064,.0283),(.066,.0274),
       (.073,.0277),(.075,.0288),(.077,.028),(.084,.0292),(.089,.031),(.093,.0333),
       (.152,.0333),(.159,.0326),(.165,.0308),(.174,.0265),(.184,.020),(.193,.0147),(.202,.0144)]
    if lod:p=[p[i] for i in [0,2,4,6,8,11,14,17,19,20,22,24,26]]
    body=lathe('Filled PET body',p,segments,'Product_PET_Kvass',lobe=.0012)
    lathe('Amber neck',[(.1838,.020),(.194,.0149),(.205,.0147)],segments,'Product_PET_Headspace')
    lathe('Genuine front label',[(.0933,.03365),(.153,.03365)],segments,'Product_Ochakovsky_Label')
    lathe('Screw cap',[(.203,.0150),(.204,.0156),(.2228,.0156),(.224,.0148)],segments,'Product_Cap_Brown',ribs=0 if lod else .00022)
    cylinder('Cap crown',.0148,.0012,.2234,'Product_Cap_Brown',segments)
    torus('Tamper band',(0,0,.2028),.0151,.0006,'Product_Cap_Brown',segments)
    cylinder('Recessed bottle bottom',.022,.001,.001,'Product_PET_Kvass',segments)
    if not lod:
        socket('Interaction_Inspect',(0,-.055,.13));socket('Socket_Grip',(0,0,.11));socket('Socket_Base',(0,0,0))

def mojito(segments,lod):
    p=[(0,.026),(.002,.0295),(.005,.0318),(.009,.033),(.151,.033),(.154,.032),(.158,.029),(.164,.027),(.166,.027)]
    lathe('Printed can wall',p,segments,'Product_Aluminium')
    lathe('Genuine printed wrap',[(.006,.0325),(.009,.03315),(.151,.03315),(.154,.03215),(.158,.02915),(.164,.02715)],segments,'Product_Mojito_Label')
    torus('Rolled top rim',(0,0,.167),.0274,.001,'Product_Aluminium',segments)
    torus('Rolled base rim',(0,0,.0017),.0273,.00085,'Product_Aluminium',segments)
    cylinder('Recessed lid',.0265,.0008,.1656,'Product_Aluminium',segments)
    cylinder('Bottom dome',.0263,.0008,.0022,'Product_Lid_Inset',segments)
    if not lod:
        torus('Lid score',(0,.006,.1662),.0085,.00018,'Product_Lid_Inset',segments,scale=(.8,1.15,1))
        torus('Pull tab',(0,-.003,.1667),.0052,.0012,'Product_Aluminium',max(16,segments//2),scale=(.8,1.55,.45))
        rivet=cylinder('Tab rivet',.0018,.0008,.167,'Product_Aluminium',max(12,segments//2));rivet.location.y=.0035
    if not lod:
        socket('Interaction_Inspect',(0,-.055,.09));socket('Socket_Grip',(0,0,.08));socket('Socket_Base',(0,0,0))

entries=[]
for id,label,kind in [('Ochakovsky_Kvass_PET_500ml','Квас «Очаковский» · ПЭТ 0,5 л','kvass'),('Mojito_Fresh_Can_450ml','Мохито Освежающий · банка 0,45 л','mojito')]:
    lod_records=[]
    for lod,segments in [(0,64),(1,24)]:
        current=bpy.data.collections.new(id+('_LOD1' if lod else ''));bpy.context.scene.collection.children.link(current)
        (kvass if kind=='kvass' else mojito)(segments,lod)
        # Fixed pieces sharing a material are one mesh: three/four renderers per LOD.
        for mat in M:
            objects=[o for o in current.objects if o.type=='MESH' and o.data.materials[0].name==mat]
            if not objects:continue
            bpy.ops.object.select_all(action='DESELECT')
            for o in objects:o.select_set(True)
            bpy.context.view_layer.objects.active=objects[0]
            if len(objects)>1:bpy.ops.object.join()
            o=bpy.context.object;o.name=id+'_'+mat
            bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.object.select_all(action='DESELECT')
        for o in current.objects:o.select_set(True)
        file=MODELS/('LOD1/'+id+'_LOD1.fbx' if lod else id+'.fbx')
        bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False)
        triangles=sum(len(p.vertices)-2 for o in current.objects if o.type=='MESH' for p in o.data.polygons)
        coordinates=[o.matrix_world@Vector(v) for o in current.objects if o.type=='MESH' for v in o.bound_box]
        low=[min(v[i] for v in coordinates) for i in range(3)];high=[max(v[i] for v in coordinates) for i in range(3)]
        record=dict(path='Products/Models/'+str(file.relative_to(MODELS)),triangles=triangles,sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        lod_records.append(record)
    entries.append(dict(id=id,label=label,category='Products',reference='official product photography',collision='capsule',grid=.01,
        size=[round(high[i]-low[i],5) for i in [0,2,1]],path=lod_records[0]['path'],lodPath=lod_records[1]['path'],
        triangles=lod_records[0]['triangles'],lodTriangles=lod_records[1]['triangles'],sha256=lod_records[0]['sha256'],lodSha256=lod_records[1]['sha256'],
        renderers=4 if kind=='kvass' else 3,license='Original geometry; official product artwork retained by Ochakovo',
        status='game-ready stylized reconstruction from front photography; rear print unavailable',
        sockets=['Interaction_Inspect','Socket_Grip','Socket_Base']))

(OUT/'catalog.json').write_text(json.dumps(dict(version=1,units='metres',assets=entries,materials=specs),ensure_ascii=False,indent=2))
(DOC/'products/catalog.json').write_text((OUT/'catalog.json').read_text())

# Editable source has the two products at native scale, with LOD1 collections hidden.
for c in bpy.data.collections:
    c.hide_render=c.name.endswith('_LOD1');c.hide_viewport=c.name.endswith('_LOD1')
    if 'Mojito' in c.name:
        for o in c.objects:o.location.x+=.11
source=Path(__file__).resolve().parent/'products.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(source))

# True product renders from the same meshes. No packshot planes/billboards.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True
scene.view_settings.view_transform='AgX';scene.world.color=(.3,.3,.3)
rig=bpy.data.collections.new('Preview studio');scene.collection.children.link(rig)
current=rig
background=material('PreviewBackground',(.94,.93,.90),0,.25)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.0005));o=bpy.context.object
for c in list(o.users_collection):c.objects.unlink(o)
rig.objects.link(o);o.data.materials.append(background)
for name,p,power,size in [('Key',(-.3,-.5,.6),5,.45),('Strip',(.4,-.1,.5),3,.18),('Rim',(.05,.3,.45),4,.3)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);rig.objects.link(o);o.location=p;o.rotation_euler=(Vector((.05,0,.1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Product camera');camera=bpy.data.objects.new('Product camera',d);rig.objects.link(camera);d.type='ORTHO';d.clip_start=.001;d.clip_end=10
scene.camera=camera;scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
for e in entries:
    for c in bpy.data.collections:
        if c.name!='Preview studio':c.hide_render=c.name!=e['id']
    center=Vector((.11 if 'Mojito' in e['id'] else 0,0,e['size'][1]/2))
    camera.location=center+Vector((.035,-.48,.13));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=.28
    scene.render.resolution_x=700;scene.render.resolution_y=840;scene.render.filepath=str(DOC/'products'/(e['id']+'.png'));bpy.ops.render.render(write_still=True)
    # Identical render used in the search grid, with no loss of aspect ratio.
    import shutil
    shutil.copy2(scene.render.filepath,DOC/'thumbnails'/(e['id']+'.png'))
for e in entries:bpy.data.collections[e['id']].hide_render=False
camera.location=(.12,-.65,.32);camera.rotation_euler=(Vector((.055,0,.11))-camera.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=.38
scene.render.resolution_x=1440;scene.render.resolution_y=1100;scene.render.filepath=str(DOC/'products/products-preview.png')
bpy.ops.render.render(write_still=True)
print('PRODUCTS_EXPORTED',[(e['id'],e['triangles'],e['lodTriangles']) for e in entries])
