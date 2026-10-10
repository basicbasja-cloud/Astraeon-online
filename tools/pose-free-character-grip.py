"""Author one shared grip pose and fixed-camera source review for the free pilot."""
from pathlib import Path
import math
import json
import bpy
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/swordsman-production/free-master-01'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'source-master.blend'))
rig=bpy.data.objects['ASTRAEON_SourceRig']
scene=bpy.context.scene
for bone in rig.pose.bones:
    if bone.rotation_mode!='QUATERNION':
        basis=bone.matrix_basis.copy();bone.rotation_mode='QUATERNION';bone.matrix_basis=basis
if 'Silver blade' not in bpy.data.materials:
    m=bpy.data.materials.new('Silver blade');m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(.58,.63,.69,1)
    p.inputs['Metallic'].default_value=.72
    p.inputs['Roughness'].default_value=.26

def rotate_bone_world(name,q):
    b=rig.pose.bones[name]
    m=q.to_matrix().to_4x4() @ b.matrix
    m.translation=b.head
    b.matrix=m
    bpy.context.view_layer.update()

index=rig.pose.bones['finger2-1.R'].head.copy()
little=rig.pose.bones['finger5-1.R'].head.copy()
blade_axis=Vector((-.12,-.52,-1)).normalized()
rotate_bone_world('wrist.R',(index-little).normalized().rotation_difference(blade_axis))
names=['finger%d-1.R'%f for f in range(2,6)]
palm=sum((rig.pose.bones[n].head for n in names),Vector())/4-rig.pose.bones['wrist.R'].head
u=(palm-blade_axis*palm.dot(blade_axis)).normalized()
v=Vector((0,-1,0));v=(v-blade_axis*v.dot(blade_axis)).normalized()
roll=math.atan2(blade_axis.dot(u.cross(v)),u.dot(v))
rotate_bone_world('wrist.R',Quaternion(blade_axis,roll))
center=sum((rig.pose.bones[n].head for n in names),Vector())/4
finger_direction=sum(((rig.pose.bones['finger%d-3.R'%f].tail-rig.pose.bones['finger%d-1.R'%f].head).normalized() for f in range(2,6)),Vector()).normalized()
finger_direction=(finger_direction-blade_axis*finger_direction.dot(blade_axis)).normalized()
palm_normal=blade_axis.cross(finger_direction).normalized()
center += finger_direction*.022+palm_normal*.006
radius=.010
finger_receipts={}

# CCD starts with a palm-plane curl, then corrects the three-dimensional
# endpoint. Incremental rotations are bounded; anatomical review remains a gate.
for finger in range(2,6):
    chain=['finger%d-%d.R'%(finger,j) for j in range(1,4)]
    base=rig.pose.bones[chain[0]].head.copy()
    h=center+blade_axis*(base-center).dot(blade_axis)
    target=h-finger_direction*.003+palm_normal*.017
    angles={name:0.0 for name in chain}
    for name in chain:
        rotate_bone_world(name,Quaternion(blade_axis,.65));angles[name]=.65
    for iteration in range(28):
        for name in reversed(chain):
            joint=rig.pose.bones[name].head.copy()
            tip=rig.pose.bones[chain[-1]].tail.copy()
            u=tip-joint;v=target-joint
            if u.length<1e-6 or v.length<1e-6:continue
            q=u.normalized().rotation_difference(v.normalized())
            if q.angle>.22:q=Quaternion(q.axis,.22)
            rotate_bone_world(name,q)
    tip=rig.pose.bones[chain[-1]].tail
    radial=tip-center-blade_axis*(tip-center).dot(blade_axis)
    finger_receipts[str(finger)]={'tip':list(tip),'target':list(target),'tipTargetError':(tip-target).length,'distanceFromHiltAxis':radial.length,'jointRotationQuaternions':{name:list(rig.pose.bones[name].rotation_quaternion) for name in chain}}

thumb_chain=['finger1-%d.R'%j for j in range(1,4)]
target=center+blade_axis*.022-palm_normal*.016
for iteration in range(24):
    for name in reversed(thumb_chain):
        joint=rig.pose.bones[name].head.copy()
        u=rig.pose.bones[thumb_chain[-1]].tail-joint;v=target-joint
        if u.length<1e-6 or v.length<1e-6:continue
        q=u.normalized().rotation_difference(v.normalized())
        if q.angle>.20:q=Quaternion(q.axis,.20)
        rotate_bone_world(name,q)
finger_receipts['thumb']={'tipTargetError':(rig.pose.bones[thumb_chain[-1]].tail-target).length,'target':list(target)}

rest_to_pose=rig.pose.bones['wrist.R'].matrix @ rig.data.bones['wrist.R'].matrix_local.inverted()
pose_to_rest=rest_to_pose.inverted()
blade_width=blade_axis.cross(Vector((0,-1,0))).normalized()
blade_normal=blade_width.cross(blade_axis).normalized()

def part(name,verts,faces,material):
    data=bpy.data.meshes.new(name)
    data.from_pydata([pose_to_rest @ Vector(p) for p in verts],[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    obj.data.materials.append(bpy.data.materials[material])
    group=obj.vertex_groups.new(name='wrist.R');group.add(list(range(len(verts))),1,'REPLACE')
    obj.modifiers.new('Right-hand socket binding','ARMATURE').object=rig
    obj.parent=rig;obj['logical_layer']='Weapon';obj['socket']='hand_R'
    return obj

def cyl(name,c,axis,length,r,material,n=20):
    x=axis.cross(Vector((0,0,1))).normalized()
    if x.length<.1:x=Vector((1,0,0))
    y=axis.cross(x).normalized()
    verts=[]
    for k in [-.5,.5]:
        for i in range(n):verts.append(tuple(c+axis*length*k+(x*math.cos(i*math.tau/n)+y*math.sin(i*math.tau/n))*r))
    faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    faces.extend([tuple(reversed(range(n))),tuple(n+i for i in range(n))])
    return part(name,verts,faces,material)

cyl('Sword hilt under fingers',center,blade_axis,.10,radius,'Brown leather')
cyl('Sword pommel',center-blade_axis*.064,blade_axis,.023,.018,'Gold edges')
guard=center+blade_axis*.06
cyl('Sword crossguard',guard,blade_width,.135,.012,'Gold edges')
cyl('Sword guard collar',guard,blade_axis,.030,.020,'Gold edges')
vertices=[]
for t,half_width in [(0,.022),(.07,.026),(.32,.017),(.43,0.001)]:
    c=guard+blade_axis*(.018+t)
    vertices.extend([tuple(c-blade_width*half_width),tuple(c+blade_normal*.009),tuple(c+blade_width*half_width),tuple(c-blade_normal*.009)])
faces=[]
for r in range(3):
    for i in range(4):faces.append((r*4+i,r*4+(i+1)%4,(r+1)*4+(i+1)%4,(r+1)*4+i))
faces.append((12,13,14,15))
blade=part('Original ASTRAEON sword blade',vertices,faces,'Silver blade')
blade['length']=.43
alt_vertices=[]
for t,half_width in [(0,.027),(.055,.041),(.255,.025),(.34,.001)]:
    c=guard+blade_axis*(.018+t)
    alt_vertices.extend([tuple(c-blade_width*half_width),tuple(c+blade_normal*.009),tuple(c+blade_width*half_width),tuple(c-blade_normal*.009)])
alt_blade=part('Alternate sword blade',alt_vertices,faces,'Silver blade')
alt_blade['variant']='alternate';alt_blade.hide_render=True

# Bind sockets as real non-deforming bones, so motion can reuse their names.
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
socket_defs={
    'root':((0,0,0),None),
    'head':(tuple(rig.data.edit_bones['head'].head),'head'),
    'hand_R':(tuple(pose_to_rest@center),'wrist.R'),
    'hand_L':(tuple(rig.data.edit_bones['wrist.L'].tail),'wrist.L'),
    'back':((0,.12,.86),'spine01'),
    'waist':((0,0,.65),'spine04'),
}
for name,(location,parent) in socket_defs.items():
    b=rig.data.edit_bones.new('socket_'+name);b.head=location;b.tail=b.head+Vector((0,0,.025));b.use_deform=False
    if parent:b.parent=rig.data.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
for b in rig.pose.bones:
    if b.rotation_mode!='QUATERNION':
        basis=b.matrix_basis.copy();b.rotation_mode='QUATERNION';b.matrix_basis=basis
    b.keyframe_insert(data_path='rotation_quaternion',frame=1,group=b.name)
    b.keyframe_insert(data_path='location',frame=1,group=b.name)
    b.keyframe_insert(data_path='scale',frame=1,group=b.name)
rig.animation_data.action.name='SourceGrip_ReviewPose'
scene.frame_set(1)

camera=scene.camera
elevation=math.radians(25)
up=Vector((0,math.sin(elevation),math.cos(elevation)))
directions=[('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',-315)]
projected_heights=[]
for name,yaw in directions:
    rig.rotation_euler.z=math.radians(yaw);bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    positions=[]
    for obj in bpy.data.objects:
        if obj.type=='MESH' and not obj.hide_render and obj.get('logical_layer') in ('BaseBody','Outfit','Hair','Face'):
            evaluated=obj.evaluated_get(graph)
            positions.extend(up.dot(evaluated.matrix_world@v.co) for v in evaluated.data.vertices)
    projected_heights.append(max(positions)-min(positions))
# One scale chosen for the whole source; there is no per-view alpha-bound fitting.
scale=max(projected_heights)*320/176
rig.rotation_euler.z=0;bpy.context.view_layer.update()
center_camera=up*((264-160)/320*scale)
camera.location=Vector((0,-4*math.cos(elevation),4*math.sin(elevation)))+center_camera
camera.rotation_euler=(center_camera-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.ortho_scale=scale
scene.render.resolution_x=320;scene.render.resolution_y=320
scene.render.resolution_percentage=100

def project(p):
    uv=world_to_camera_view(scene,camera,rig.matrix_world@Vector(p))
    return [uv.x*320,(1-uv.y)*320]

views=[]
OUT.joinpath('grip-review').mkdir(exist_ok=True)
for name,yaw in directions:
    rig.rotation_euler.z=math.radians(yaw);bpy.context.view_layer.update()
    sockets={n:project(rig.pose.bones['socket_'+n].head) for n in socket_defs}
    scene.render.filepath=str(OUT/'grip-review'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    views.append({'direction':name,'yawDegrees':yaw,'sockets':sockets,'root':project((0,0,0))})

# Repeat the stress view using precisely the same rig/camera, then compare bytes outside Blender.
rig.rotation_euler.z=math.radians(-135);bpy.context.view_layer.update()
scene.render.filepath=str(OUT/'grip-review'/'NW-repeat.png');bpy.ops.render.render(write_still=True)
blade.hide_render=True;alt_blade.hide_render=False
for name,yaw in [('NW',-135),('SE',-315)]:
    rig.rotation_euler.z=math.radians(yaw);bpy.context.view_layer.update()
    scene.render.filepath=str(OUT/'grip-review'/('alternate-sword-'+name+'.png'));bpy.ops.render.render(write_still=True)
blade.hide_render=False;alt_blade.hide_render=True

# Outfit removal is a source geometry proof, not a final BaseBody sprite sheet.
rig.rotation_euler.z=math.radians(-315);bpy.context.view_layer.update()
hidden=[]
coverage=bpy.data.objects['CanonicalBody'].modifiers.get('Glove coverage holdout')
if coverage:coverage.show_render=False
for o in bpy.data.objects:
    if o.get('logical_layer') in ('Outfit','Cape','Weapon') or any(word in o.name for word in ['Bronze','belt','Buckle','Scarf','Sculpted boot']):
        if not o.hide_render:hidden.append(o);o.hide_render=True
scene.render.filepath=str(OUT/'grip-review'/'body-without-outfit.png');bpy.ops.render.render(write_still=True)
for o in hidden:o.hide_render=False
if coverage:coverage.show_render=True

# Large orthographic grip detail, without changing the source skeleton or fingers.
saved_camera=camera.matrix_world.copy();saved_scale=camera.data.ortho_scale
inspection_visibility={o.name:o.hide_render for o in bpy.data.objects if o.type=='MESH'}
glove=bpy.data.objects['Gloves with articulated fingers']
right_group=glove.vertex_groups.new(name='Inspection right hand')
right_group.add([v.index for v in glove.data.vertices if v.co.x<0],1,'REPLACE')
right_mask=glove.modifiers.new('Inspect right hand only','MASK');right_mask.vertex_group=right_group.name
for o in bpy.data.objects:
    if o.type=='MESH':
        o.hide_render=not(o==glove or o.name=='Bronze bracer.R' or (o.get('logical_layer')=='Weapon' and o.get('variant')!='alternate'))
for name,yaw in [('W',-90),('NW',-135),('N',-180),('SE',-315)]:
    rig.rotation_euler.z=math.radians(yaw);bpy.context.view_layer.update()
    hand=rig.matrix_world@rig.pose.bones['socket_hand_R'].head
    camera.location=hand+Vector((0,-1,.38))
    camera.rotation_euler=(hand-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=.28
    scene.render.resolution_x=640;scene.render.resolution_y=640
    scene.render.filepath=str(OUT/'grip-review'/('hand-'+name+'.png'));bpy.ops.render.render(write_still=True)
for name,hidden in inspection_visibility.items():bpy.data.objects[name].hide_render=hidden
glove.modifiers.remove(right_mask);glove.vertex_groups.remove(right_group)
camera.matrix_world=saved_camera;camera.data.ortho_scale=saved_scale
scene.render.resolution_x=320;scene.render.resolution_y=320
rig.rotation_euler.z=0;bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'grip-master.blend'))
receipt={'status':'SOURCE_GRIP_PILOT_UNAPPROVED','fingers':finger_receipts,'hiltCenter':list(center),'hiltRadius':radius,'bladeAxisInCharacterSpace':list(blade_axis),'camera':{'elevationDegrees':25,'orthographicScale':scale,'matrix':[list(r) for r in camera.matrix_world],'scaleRule':'Single scale across eight views, max source body/outfit/head height -> 176 px'},'canvas':{'width':320,'height':320,'root':[160,264],'referenceHeight':176},'views':views,'paidCalls':0,'handCloseups':'Right glove, right bracer and sword isolated for inspection. Other anatomy, outfit and cape hidden; complete views keep real occlusion','limitations':['Geometry source pilot; final painted style not achieved','Costume intersections and face identity need visual review','No motion coverage or runtime package claimed']}
(OUT/'grip-proof.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('GRIP_SOURCE_READY',str(OUT/'grip-master.blend'))
