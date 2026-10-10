"""Fresh MPFB-based, connected source pilot. Blender authoring only.

Run with Blender --background --factory-startup --python-exit-code 1 --python.
Approved concept is reference only. No rejected character sources are imported.
"""
from pathlib import Path
import math
import json
import bpy
from mathutils import Vector, Matrix, Quaternion

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'authoring/characters/swordsman-production/free-master-01'
OUT.mkdir(parents=True, exist_ok=True)
TOOLS = ROOT / '.character-tools/mpfb-2.0.17/mpfb2-2.0.17/src'
bpy.context.preferences.extensions.repos.new(name='ASTRAEON local tools', module='character_local', custom_directory=str(TOOLS))
bpy.ops.preferences.addon_enable(module='bl_ext.character_local.mpfb')
from bl_ext.character_local.mpfb.services.humanservice import HumanService
from bl_ext.character_local.mpfb.services.targetservice import TargetService

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, rgb, metal=0, rough=.65):
    m = bpy.data.materials.new(name)
    m.use_fake_user = True
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

skin = material('Skin warm ivory', (.66,.36,.21))
navy = material('Navy cloth', (.028,.033,.058))
olive = material('Olive trousers', (.07,.077,.045))
leather = material('Brown leather', (.095,.042,.021))
hair_mat = material('Silver lavender hair', (.37,.32,.40))
ivory = material('Ivory tunic', (.72,.63,.43))
gold = material('Bronze armor', (.43,.22,.07), .55, .36)
gold_trim = material('Gold edges', (.70,.40,.12), .65, .30)
mustard = material('Mustard scarf and cape', (.72,.34,.026))
teal = material('Teal hip sash', (.022,.19,.20))
steel = material('Silver blade', (.58,.63,.69), .72,.26)
eye_white = material('Eye white', (.75,.73,.63))
iris_mat = material('Gray blue iris', (.055,.073,.095))
pupil_mat = material('Pupil and brow', (.012,.009,.014))

macro = TargetService.get_default_macro_info_dict()
macro.update(gender=1.0, age=.35, muscle=.4, weight=.45)
macro['race'] = {'asian': .7, 'caucasian': .3, 'african': 0}
body = HumanService.create_human(macro_detail_dict=macro)
body.name = 'CanonicalBody'
targets = TOOLS / 'mpfb/data/targets'
target_weights = {
    'head/head-age-decr': .5,
    'head/head-round': .35,
    'nose/nose-scale-depth-decr': 1.0,
    'nose/nose-volume-decr': .55,
    'chin/chin-width-decr': .3,
    'chin/chin-triangle': .45,
    'mouth/mouth-lowerlip-volume-decr': .7,
    'mouth/mouth-upperlip-volume-decr': .7,
    'eyes/l-eye-scale-incr': 1.15,
    'eyes/r-eye-scale-incr': 1.15,
}
for name, weight in target_weights.items():
    file = targets / (name + '.target.gz')
    if not file.exists():
        raise FileNotFoundError(file)
    TargetService.load_target(body, str(file), weight=weight)

bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
body_group_index = body.vertex_groups['body'].index
skin_ids = [v.index for v in body.data.vertices if any(g.group==body_group_index and g.weight>.5 for g in v.groups)]
source_height = max(body.data.vertices[i].co.z for i in skin_ids)
normalization = 1.4014367/source_height
for v in body.data.vertices: v.co *= normalization
original = [v.co.copy() for v in body.data.vertices]

def smoothstep(a,b,x):
    t = min(1, max(0,(x-a)/(b-a)))
    return t*t*(3-2*t)

def compact(p):
    x,y,z = p
    # An uninterrupted anatomical surface, including the concealed torso and hands.
    # Head/neck transition is continuous; no independent limb-image assembly.
    z_new = z*.77
    head_mix = smoothstep(1.16,1.24,z)
    z_head = .94 + (z-1.20)*1.85
    z_new = z_new*(1-head_mix) + z_head*head_mix
    width = 1.25*(1-head_mix) + 1.85*head_mix
    depth = 1.25*(1-head_mix) + 1.65*head_mix
    point=Vector((x*width,y*depth,z_new))
    arm_mix=smoothstep(.12,.20,abs(x))*(1-smoothstep(1.11,1.16,z))*smoothstep(.67,.74,z)
    shoulder=Vector((math.copysign(.185,x),-.0175,.84))
    shortened=shoulder+(point-shoulder)*.75
    return point.lerp(shortened,arm_mix)

for v in body.data.vertices:
    v.co = compact(v.co)
body.shape_key_add(name='Compact source')
foundation_key = body.shape_key_add(name='Unshaped MPFB foundation')
for i,p in enumerate(original):
    foundation_key.data[i].co = p
foundation_key.value = 0
rig = HumanService.add_builtin_rig(body,'default_no_toes')
for bone in rig.pose.bones: bone.rotation_mode='QUATERNION'
rig.name = 'ASTRAEON_SourceRig'
rig.show_in_front = True
rig['status'] = 'SOURCE_PILOT_NOT_APPROVED'
rig['source'] = 'MPFB 2.0.17 CC0 mesh and weights; custom compact shape'
body['runtime_role'] = 'AUTHORING_ONLY'
body['logical_layer'] = 'BaseBody'

for m in (skin,navy,olive,leather):
    body.data.materials.append(m)
for poly in body.data.polygons:
    p = sum((original[i] for i in poly.vertices),Vector())/len(poly.vertices)
    # Temporary modesty/underlayer materials. Separate fitted clothing follows.
    poly.material_index = 1 if .67<p.z<.79 and abs(p.x)<.15 else 0
    poly.use_smooth = True
sub = body.modifiers.new('Skin subdivision','SUBSURF')
sub.levels = 1
sub.render_levels = 1

def mesh(name,verts,faces,mat,bone=None):
    data=bpy.data.meshes.new(name)
    data.from_pydata(verts,[],faces)
    data.update()
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj['logical_layer']='Outfit'
    for p in data.polygons: p.use_smooth=True
    if bone:
        group=obj.vertex_groups.new(name=bone)
        group.add(list(range(len(data.vertices))),1,'REPLACE')
        mod=obj.modifiers.new('Shared source rig','ARMATURE'); mod.object=rig
        obj.parent=rig
    return obj

def ellipsoid(name,center,size,mat,bone):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=center)
    obj=bpy.context.object; obj.name=name
    obj.scale=size
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    obj.data.materials.append(mat)
    obj['logical_layer']='Face'
    for p in obj.data.polygons:p.use_smooth=True
    group=obj.vertex_groups.new(name=bone);group.add(list(range(len(obj.data.vertices))),1,'REPLACE')
    obj.modifiers.new('Shared source rig','ARMATURE').object=rig
    obj.parent=rig
    return obj

for side in ('L','R'):
    c=rig.data.bones['eye.'+side].head_local.copy()
    c.y-=.007
    eye=ellipsoid('Eye.'+side,c,(.033,.030,.025),eye_white,'head')
    ellipsoid('Iris.'+side,c+Vector((0,-.027,0)),(.016,.005,.020),iris_mat,'head')
    ellipsoid('Pupil.'+side,c+Vector((0,-.031,0)),(.007,.002,.013),pupil_mat,'head')
    ellipsoid('Eye highlight.'+side,c+Vector((-.005,-.034,.008)),(.004,.001,.005),eye_white,'head')

def shell(name,predicate,mat,offset=.01):
    # Copy contiguous anatomical faces, preserving their exact bone weights.
    body_group=body.vertex_groups['body'].index
    body_ids={v.index for v in body.data.vertices if any(g.group==body_group and g.weight>.5 for g in v.groups)}
    faces=[p for p in body.data.polygons if all(i in body_ids for i in p.vertices) and predicate(sum((original[i] for i in p.vertices),Vector())/len(p.vertices))]
    ids=sorted({i for p in faces for i in p.vertices});mapping={old:new for new,old in enumerate(ids)}
    obj=mesh(name,[body.data.vertices[i].co+body.data.vertices[i].normal*offset for i in ids],[[mapping[i] for i in p.vertices] for p in faces],mat)
    for g in body.vertex_groups:
        if g.name in rig.data.bones:
            ng=obj.vertex_groups.new(name=g.name)
            for i in ids:
                for vg in body.data.vertices[i].groups:
                    if vg.group==g.index:ng.add([mapping[i]],vg.weight,'REPLACE')
    obj.parent=rig
    obj.modifiers.new('Shared source rig','ARMATURE').object=rig
    sub=obj.modifiers.new('Cloth smoothing','SUBSURF');sub.levels=1
    solid=obj.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.006
    obj['logical_layer']='Outfit'
    return obj

shell('Navy fitted shirt',lambda p: .735<p.z<1.16 and abs(p.x)<.34,navy,.012)
shell('Olive fitted trousers',lambda p: .27<p.z<.76 and abs(p.x)<.24,olive,.012)
shell('Brown fitted boots',lambda p: p.z<.30,leather,.014)
gloves=shell('Gloves with articulated fingers',lambda p: abs(p.x)>.37 and .70<p.z<.88,leather,.010)
# The concealed body remains editable. This reversible source mask avoids
# skin/glove interpenetration in this posed inspection; it is not a runtime layer.
glove_group=body.vertex_groups.new(name='Concealed by gloves')
glove_ids=[i for i,p in enumerate(original) if abs(p.x)>.365 and .695<p.z<.895]
glove_group.add(glove_ids,1,'REPLACE')
glove_mask=body.modifiers.new('Glove coverage holdout','MASK');glove_mask.vertex_group=glove_group.name;glove_mask.invert_vertex_group=True

def band(name,z,width,depth,height,mat,bone='spine05'):
    verts=[];faces=[];n=48
    for zz in (z-height/2,z+height/2):
        for i in range(n):
            a=2*math.pi*i/n;verts.append((width*math.sin(a),depth*math.cos(a),zz))
    for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    obj=mesh(name,verts,faces,mat,bone)
    solid=obj.modifiers.new('Band thickness','SOLIDIFY');solid.thickness=.009
    return obj

band('Leather belt',.66,.18,.17,.060,leather,'spine04')
band('Scarf collar',.927,.13,.105,.080,mustard,'neck01')

def cube(name,center,size,mat,bone):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    o=bpy.context.object;o.name=name;o.scale=size
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    o.data.materials.append(mat)
    o['logical_layer']='Outfit'
    bev=o.modifiers.new('Soft bevel','BEVEL');bev.width=.008;bev.segments=3
    g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
    o.modifiers.new('Shared source rig','ARMATURE').object=rig;o.parent=rig
    return o

cube('Bronze belt buckle',(0,-.179,.66),(.065,.014,.052),gold_trim,'spine04')
cube('Buckle inset',(0,-.190,.66),(.042,.006,.031),leather,'spine04')

def panel(name,points,mat,bone):
    obj=mesh(name,points,[tuple(range(len(points)))],mat,bone)
    solid=obj.modifiers.new('Fabric volume','SOLIDIFY');solid.thickness=.008
    bevel=obj.modifiers.new('Fabric edge','BEVEL');bevel.width=.008;bevel.segments=2
    obj['logical_layer']='Outfit'
    return obj

panel('Ivory split tunic R',[(-.155,-.155,.655),(-.005,-.175,.655),(-.026,-.205,.405),(-.205,-.18,.435)],ivory,'spine05')
panel('Ivory split tunic L',[(.005,-.175,.655),(.155,-.155,.655),(.205,-.18,.435),(.026,-.205,.405)],ivory,'spine05')
panel('Teal left hip sash',[(.145,-.18,.65),(.225,-.12,.63),(.245,-.17,.41),(.155,-.22,.43)],teal,'pelvis.L')
panel('Rear tunic panel',[(-.155,.16,.64),(.155,.16,.64),(.19,.20,.425),(-.19,.20,.425)],ivory,'spine05')
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
chest_verts=[];chest_faces=[]
for j in range(13):
    z=.686+j/12*.206
    for i in range(9):
        x=(i/8*2-1)*(.056+.009*j/12)
        hit=surface.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)[0]
        if hit is None:raise RuntimeError('Chest panel misses body surface')
        chest_verts.append((x,hit.y-.019,z))
for j in range(12):
    for i in range(8):chest_faces.append((j*9+i,j*9+i+1,(j+1)*9+i+1,(j+1)*9+i))
chest=mesh('Ivory sewn chest insert',chest_verts,chest_faces,ivory,'spine02');chest['logical_layer']='Outfit'
chest.modifiers.new('Panel thickness','SOLIDIFY').thickness=.006

def loft(name,rings,mat,bone):
    n=len(rings[0]);verts=[p for ring in rings for p in ring]
    faces=[]
    for r in range(len(rings)-1):
        for i in range(n):faces.append((r*n+i,r*n+(i+1)%n,(r+1)*n+(i+1)%n,(r+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))])
    return mesh(name,verts,faces,mat,bone)

# Closed sculpted shoe volumes cover all toe topology; editable feet remain underneath.
for side in ('R','L'):
    ankle=rig.data.bones['foot.'+side].head_local
    rings=[]
    for z,rx,ry,cy in [(.010,.095,.164,-.080),(.035,.095,.164,-.080),(.075,.087,.151,-.070),(.113,.055,.067,-.012)]:
        rings.append([(ankle.x+rx*math.sin(i*math.tau/24),cy+ry*math.cos(i*math.tau/24),z) for i in range(24)])
    shoe=loft('Sculpted boot foot.'+side,rings,leather,'foot.'+side)
    bev=shoe.modifiers.new('Rounded shoe edges','BEVEL');bev.width=.013;bev.segments=3

# Shoulder plates are volumetric open shells over the rig's real shoulder surface.
for side,sgn in [('R',-1),('L',1)]:
    center=rig.data.bones['upperarm01.'+side].head_local
    verts=[];faces=[];n=32
    for j in range(9):
        t=(j+.05)*math.pi/2/9
        for i in range(n):
            a=i*math.tau/n
            verts.append(tuple(center+Vector((.095*math.sin(t)*math.cos(a),.090*math.sin(t)*math.sin(a),.065*math.cos(t)))))
    for j in range(8):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    o=mesh('Bronze pauldron.'+side,verts,faces,gold,'upperarm01.'+side)
    o.modifiers.new('Armor thickness','SOLIDIFY').thickness=.008
    rim=[]
    for dz in [0,.009]:
        rim.append([tuple(center+Vector((.097*math.cos(i*math.tau/32),.092*math.sin(i*math.tau/32),.012+dz))) for i in range(32)])
    loft('Pauldron gold rim.'+side,rim,gold_trim,'upperarm01.'+side)
    forearm=rig.data.bones['lowerarm01.'+side]
    wrist=rig.data.bones['wrist.'+side].head_local
    axis=(wrist-forearm.head_local).normalized()
    cross=axis.cross(Vector((0,1,0))).normalized();normal=axis.cross(cross).normalized()
    rings=[]
    for t,radius in [(0.15,.047),(.20,.052),(.65,.042),(.86,.036)]:
        c=forearm.head_local.lerp(wrist,t)
        rings.append([tuple(c+(cross*math.cos(i*math.tau/24)+normal*math.sin(i*math.tau/24))*radius) for i in range(24)])
    bracer=loft('Bronze bracer.'+side,rings,gold,'lowerarm01.'+side)
    bracer.modifiers.new('Armor edge bevel','BEVEL').width=.006

def strand(name,path,width,mat):
    verts=[];faces=[];n=8
    for k,p in enumerate(path):
        p=Vector(p)
        direction=Vector(path[min(k+1,len(path)-1)])-Vector(path[max(k-1,0)])
        direction.normalize()
        axis=direction.cross(Vector((0,-1,0))).normalized()
        if axis.length<.1:axis=Vector((1,0,0))
        normal=direction.cross(axis).normalized()
        radius=width*[.50,1.0,.70,.015][k]
        for i in range(n):
            a=i*math.tau/n
            verts.append(tuple(p+axis*math.cos(a)*radius+normal*math.sin(a)*radius*.30))
    for k in range(len(path)-1):
        for i in range(n):faces.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
    faces.append(tuple(reversed(range(n))))
    obj=mesh(name,verts,faces,mat,'head')
    obj['logical_layer']='Hair'
    sub=obj.modifiers.new('Sculpted hair smoothing','SUBSURF');sub.levels=1
    return obj

# Full scalp surface and individually editable swept locks; no flat image cards.
hair_center=Vector((0,-.056,1.140))
verts=[];faces=[];n=48
for j in range(11):
    for i in range(n):
        a=i*math.tau/n
        bottom=1.30 if math.sin(a)<-.6 else 1.65
        t=.02+j*bottom/10
        verts.append(tuple(hair_center+Vector((.164*math.sin(t)*math.cos(a),.155*math.sin(t)*math.sin(a),.205*math.cos(t)))))
for j in range(10):
    for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
cap=mesh('Hair scalp volume',verts,faces,hair_mat,'head');cap['logical_layer']='Hair'
for i in range(9):
    x=(i-4)*.034
    tip_height=1.175+.015*math.sin(i*1.7)
    strand('Swept fringe %02d'%i,[(x*.45,-.100,1.330),(x*.8,-.200,1.278),(x+.020,-.220,1.230),(x+.028,-.232,tip_height)],.039,hair_mat)
for i in range(18):
    a=i*math.tau/18
    radial=Vector((math.cos(a),math.sin(a),0))
    strand('Side and back lock %02d'%i,[tuple(hair_center+radial*.05+Vector((0,0,.19))),tuple(hair_center+radial*.135+Vector((0,0,.115))),tuple(hair_center+radial*.170+Vector((0,0,.045))),tuple(hair_center+radial*.204+Vector((0,0,-.045+(.025 if i%2 else 0))))],.034,hair_mat)
strand('Crown sweep',[(.02,.02,1.30),(-.025,.013,1.355),(-.065,.005,1.390),(-.092,-.007,1.410)],.035,hair_mat)
for i in range(8):
    side=-1 if i<4 else 1;t=i%4
    y=-.13+t*.052
    strand('Tousled crown layer %02d'%i,[(side*.012,y,1.327),(side*.082,y-.02,1.357),(side*.157,y+.008,1.332),(side*(.19+.012*t),y+.025,1.354-.013*t)],.037,hair_mat)

# Scarf lies across the chest. Cape is a continuous curved rear cloth surface.
scarf_verts=[];scarf_faces=[]
for j in range(6):
    for i in range(33):
        a=i*math.tau/32;t=j/5
        rx=.12+.04*t;ry=.10+.025*t
        scarf_verts.append((rx*math.sin(a),ry*math.cos(a),.94-.082*t*(1.0-.32*math.cos(a))+.006*math.sin(a*3+t)))
for j in range(5):
    for i in range(32):scarf_faces.append((j*33+i,j*33+i+1,(j+1)*33+i+1,(j+1)*33+i))
scarf=mesh('Draped scarf',scarf_verts,scarf_faces,mustard,'spine01');scarf['logical_layer']='Cape'
scarf.modifiers.new('Fold thickness','SOLIDIFY').thickness=.012
cape_verts=[];cape_faces=[]
for j in range(13):
    t=j/12
    for i in range(17):
        u=i/16*2-1
        cape_verts.append((u*(.11+.14*t)-.05*t,.11+.10*t+.02*math.cos(u*math.pi*3)*t,.91-.48*t+.03*abs(u)*t))
for j in range(12):
    for i in range(16):cape_faces.append((j*17+i,j*17+i+1,(j+1)*17+i+1,(j+1)*17+i))
cape=mesh('Mustard cape source',cape_verts,cape_faces,mustard,'spine01');cape['logical_layer']='Cape'
cape.modifiers.new('Cloth thickness','SOLIDIFY').thickness=.010
cape.modifiers.new('Cloth smoothing','SUBSURF').levels=1

# Anatomical source-pose utilities: geometry follows the same weighted rig.
def point_bone(name,direction):
    bpy.context.view_layer.update()
    b=rig.pose.bones[name]
    q=(b.tail-b.head).normalized().rotation_difference(Vector(direction).normalized())
    m=q.to_matrix().to_4x4() @ b.matrix
    m.translation=b.head
    b.matrix=m
    bpy.context.view_layer.update()

for side,sgn in (('R',-1),('L',1)):
    point_bone('upperarm01.'+side,(sgn*.16,0,-1))
    point_bone('lowerarm01.'+side,(sgn*.13,-.06,-1))

scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.world.color=(.17,.17,.17)
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'

def track(obj,point):obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-4,2.05))
cam=bpy.context.object;cam.name='LockedOrthographicCamera';cam.data.type='ORTHO';cam.data.ortho_scale=2.05
track(cam,(0,0,.69));scene.camera=cam
for name,loc,power,size in [('Key',(-3,-4,5),450,4),('Fill',(3,-2,3),200,3),('Rim',(1,3,4),400,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    light=bpy.context.object;light.name=name;light.data.energy=power;light.data.shape='DISK';light.data.size=size;track(light,(0,0,.7))

OUT.joinpath('previews').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source-master.blend'))
for direction,degrees in [('S',0),('W',-90),('N',-180),('SE',-315)]:
    rig.rotation_euler.z=math.radians(degrees)
    scene.render.filepath=str(OUT/'previews'/('source-'+direction+'.png'))
    bpy.ops.render.render(write_still=True)
rig.rotation_euler.z=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source-master.blend'))
(OUT/'build-spec.json').write_text(json.dumps({'status':'SOURCE_PILOT_NOT_APPROVED','mpfbVersion':'2.0.17','macro':macro,'targets':target_weights,'cameraMatrix':list(sum((list(r) for r in cam.matrix_world),[])),'previewSize':[640,640],'renderEngine':scene.render.engine,'paidCalls':0},indent=2),encoding='utf-8')
print('SOURCE_MASTER_BUILT',str(OUT/'source-master.blend'))
