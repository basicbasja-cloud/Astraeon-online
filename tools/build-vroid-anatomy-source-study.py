"""Fresh source study from a licensed anime base and native rotational hands.

Preserves the donor palm and phalanx proportions. Fits only major anatomy
segments, then applies one rigid transform to each already posed whole hand.
No new production armature, action coverage or owner approval is created.
"""
import bpy, bmesh, math, json
from mathutils import Vector, Matrix, Quaternion
donor=bpy.data.scenes['ASTRAEON_VROID_BASE_MALE_INSPECTION']
hand_study=bpy.data.scenes['ASTRAEON_ANATOMICAL_HAND_STUDY_05']
previous=bpy.data.scenes['ASTRAEON_ASSET_FIT_04']
assert bpy.data.scenes.get('ASTRAEON_ANATOMY_SOURCE_05') is None
s=bpy.data.scenes.new('ASTRAEON_ANATOMY_SOURCE_05');bpy.context.window.scene=s
s.render.engine=previous.render.engine;s.render.film_transparent=True
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.view_settings.view_transform='Standard'
root=bpy.data.objects.new('ROOT_AnatomySource05',None);s.collection.objects.link(root);root.rotation_euler.z=math.radians(45)
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}
# The unsuccessful depth experiment does not establish the new weapon pose.
P['blade_tip']=Vector(previous['swordDepthOriginalTip'])
rig=next(o for o in donor.objects if o.type=='ARMATURE')
for pb in rig.pose.bones:
    pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion();pb.scale=(1,1,1)
for pb in rig.pose.bones:
    if pb.name.startswith('J_Bip_R_') and pb.name in bpy.data.objects['RIG_DonorHandInspection05'].pose.bones:
        pb.rotation_quaternion=bpy.data.objects['RIG_DonorHandInspection05'].pose.bones[pb.name].rotation_quaternion.copy()
# Relax the empty left hand with small anatomical rotations, not a phantom grip.
for digit in ['Index','Middle','Ring','Little']:
    for i,angle in enumerate([12,18,12],1):
        rig.pose.bones['J_Bip_L_'+digit+str(i)].rotation_quaternion=Quaternion(Vector((0,0,1)),math.radians(angle))
bpy.context.window.scene=donor;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
canonical=Matrix.Rotation(math.pi,4,'Z')
points={name:canonical@bone.head_local for name,bone in rig.data.bones.items()}
mapping={};frames={}
def target(name,child,a,b,width=1):
    old=points[name];direction=points[child]-old;unit=direction.normalized()
    length=(b-a).length/direction.length;turn=direction.rotation_difference(b-a).to_matrix()
    stretch=Matrix.Identity(3)*width
    for i in range(3):
        for j in range(3):stretch[i][j]+=(length-width)*unit[i]*unit[j]
    mapping[name]=Matrix.Translation(a)@(turn@stretch).to_4x4()@Matrix.Translation(-old)
    frames[name]={'a':list(a),'b':list(b),'widthScale':width,'lengthScale':length}
target('J_Bip_C_Hips','J_Bip_C_Spine',P['pelvis'],P['waist']-Vector((0,0,.095)),1.32)
target('J_Bip_C_Spine','J_Bip_C_Chest',P['waist']-Vector((0,0,.095)),P['waist']+Vector((0,0,.073)),1.25)
target('J_Bip_C_Chest','J_Bip_C_UpperChest',P['waist']+Vector((0,0,.073)),P['chest'],1.16)
target('J_Bip_C_UpperChest','J_Bip_C_Neck',P['chest'],P['neck'],1.14)
old_head=Vector((-.00051,-.0063,1.638))
new_head=Vector((.0553,-.045,1.601))
head_transform=Matrix.Translation(new_head)@Matrix.Diagonal((1.55,1.30,1.35,1))@Matrix.Translation(-old_head)
for name in points:
    if name.startswith(('J_Adj_','J_Sec_')) or name=='J_Bip_C_Head':mapping[name]=head_transform
target('J_Bip_C_Neck','J_Bip_C_Head',P['neck'],head_transform@points['J_Bip_C_Head'],1.12)
hand_targets={}
for side in ['R','L']:
    stem='J_Bip_'+side+'_'
    if side=='R':
        axis=(P['blade_tip']-P['guard']).normalized()
        center=P['guard']-axis*.063
        longitudinal=center-P['wrist_R'];longitudinal=(longitudinal-axis*longitudinal.dot(axis)).normalized()
        dorsal=longitudinal.cross(axis).normalized()
        # Native right palm axes: +X longitudinal, +Y across, +Z dorsal.
        orientation=Matrix((longitudinal,axis,dorsal)).transposed()
        local_center=Vector((.689,.026,1.372))
        hand_transform=Matrix.Translation(center)@orientation.to_4x4()@Matrix.Translation(-local_center)
        wrist=hand_transform@rig.data.bones[stem+'Hand'].head_local
        # Hand transform consumes native donor coordinates, unlike major-frame
        # transforms which consume canonical coordinates.
        mapping[stem+'Hand']=hand_transform@canonical.inverted()
        hand_targets[side]={'wrist':list(wrist),'center':list(center),'uniformScale':1,'axis':list(axis)}
    else:
        wrist=P['wrist_L'];oldw=points[stem+'Hand'];oldm=points[stem+'Middle1']
        direction=P['palm_L']-wrist;turn=(oldm-oldw).rotation_difference(direction).to_matrix()
        mapping[stem+'Hand']=Matrix.Translation(wrist)@turn.to_4x4()@Matrix.Translation(-oldw)
        hand_targets[side]={'wrist':list(wrist),'uniformScale':1,'relaxedNotWeaponGrip':True}
    for name in points:
        if name.startswith(stem) and any(digit in name for digit in ['Index','Middle','Ring','Little','Thumb']):mapping[name]=mapping[stem+'Hand']
    target(stem+'Shoulder',stem+'UpperArm',P['neck']+Vector((-.03 if side=='R' else .03,0,-.035)),P['shoulder_'+side],1.1)
    target(stem+'UpperArm',stem+'LowerArm',P['shoulder_'+side],P['elbow_'+side],1.10)
    target(stem+'LowerArm',stem+'Hand',P['elbow_'+side],wrist,1.12)
    target(stem+'UpperLeg',stem+'LowerLeg',P['hip_'+side],P['knee_'+side],1.25)
    target(stem+'LowerLeg',stem+'Foot',P['knee_'+side],P['ankle_'+side],1.20)
    ankle=P['ankle_'+side];ball=ankle+Vector((0,-.12,-ankle.z+.023))
    target(stem+'Foot',stem+'ToeBase',ankle,ball,1.1)
    mapping[stem+'ToeBase']=mapping[stem+'Foot'];mapping[stem+'ToeBase_end']=mapping[stem+'Foot']
bpy.context.window.scene=donor;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
def fitted(obj,label):
    evaluated=obj.evaluated_get(deps)
    data=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
    copy=obj.copy();copy.data=data;copy.name='SM_Anatomy05_'+label;copy.modifiers.clear();s.collection.objects.link(copy)
    copy.parent=root;copy.matrix_parent_inverse=Matrix.Identity(4);copy.matrix_basis=Matrix.Identity(4)
    for v in data.vertices:
        co=canonical@obj.matrix_world@v.co
        weights=[(obj.vertex_groups[g.group].name,g.weight) for g in v.groups if obj.vertex_groups[g.group].name in mapping and g.weight>.00001]
        total=sum(w for name,w in weights)
        v.co=sum((mapping[name]@co*(weight/total) for name,weight in weights),start=Vector((0,0,0))) if total else co
    data.update();return copy
body0=next(o for o in donor.objects if o.type=='MESH' and o.name.startswith('Body'))
face0=next(o for o in donor.objects if o.type=='MESH' and o.name.startswith('Face'))
body=fitted(body0,'Body');face=fitted(face0,'Head')
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=0],context='FACES')
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(body.data);bm.free();body.data.update()
body.data.materials.clear();body.data.materials.append(bpy.data.materials['Fit04_StylizedSkin'])
for f in body.data.polygons:f.material_index=0;f.use_smooth=True
# Use donor skin UV and native face layers. These are not screen-projected art.
for obj in [body,face]:
    for material in obj.data.materials:
        if material:
            for node in material.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image:node.image.pack()
body['license']='VRoid Base Male beta / pixiv Inc. / CC0-1.0'
face['license']=body['license']
bpy.context.window.scene=s
camera=previous.camera.copy();camera.data=previous.camera.data.copy();camera.name='CAM_Anatomy05';s.collection.objects.link(camera);s.camera=camera
for o in previous.objects:
    if o.type=='LIGHT':
        c=o.copy();c.data=o.data.copy();c.name='Anatomy05_'+o.name;s.collection.objects.link(c)
s.world=previous.world
# Retain original ASTRAEON custom costume design geometry, excluding rejected
# body-derived anatomy/gloves/garments and the unsuccessful sword-depth test.
excluded=('Body','Eyes','Brows','Refitted_','FaceDetail_','Identity_Boot','Male_Ranger','Fitted_','ClosedGlove_','Boot_','KneeCuff_')
retained=[]
for obj in previous.objects:
    if obj.type not in ('MESH','CURVE') or obj.hide_render or not obj.name.startswith('SM_AssetFit04_'):continue
    short=obj.name.removeprefix('SM_AssetFit04_')
    if short.startswith(excluded):continue
    c=obj.copy();c.data=obj.data.copy();c.name='SM_Anatomy05_'+short;s.collection.objects.link(c);c.parent=root
    if short.startswith(('Blade_','Hilt_','Identity_Weapon')):
        backup=bpy.data.meshes.get('DepthBefore_'+obj.data.name) if obj.type=='MESH' else bpy.data.curves.get('DepthBefore_'+obj.data.name)
        if backup:c.data=backup.copy()
    retained.append(c.name)
# Clothing shells are extracted from the new coherent anatomy; palms retain
# the real donor topology and native rotational grip, not old circular fingers.
def region(poly):
    weights={}
    for i in poly.vertices:
        for g in body.data.vertices[i].groups:
            name=body.vertex_groups[g.group].name;weights[name]=weights.get(name,0)+g.weight
    name=max(weights,key=weights.get);side='R' if '_R_' in name else 'L'
    if any(digit in name for digit in ['Hand','Index','Middle','Ring','Little','Thumb']):return 'Glove_'+side
    if any(bone in name for bone in ['UpperArm','LowerArm','Shoulder']):return 'Sleeve_'+side
    if 'UpperLeg' in name:return 'Trouser_'+side
    if any(bone in name for bone in ['LowerLeg','Foot','Toe']):return 'Boot_'+side
    if name=='J_Bip_C_Head':return None
    return 'Tunic'
regions={}
for poly in body.data.polygons:
    name=region(poly)
    if name:regions.setdefault(name,[]).append(poly)
for name,polys in regions.items():
    indices=sorted({i for f in polys for i in f.vertices});remap={i:j for j,i in enumerate(indices)}
    offset=.003 if name.startswith('Glove') else .014
    verts=[body.data.vertices[i].co+body.data.vertices[i].normal*offset for i in indices]
    data=bpy.data.meshes.new('Anatomy05Cloth_'+name);data.from_pydata(verts,[],[tuple(remap[i] for i in f.vertices) for f in polys]);data.update()
    c=bpy.data.objects.new('SM_Anatomy05_Cloth_'+name,data);s.collection.objects.link(c);c.parent=root
    old=bpy.data.objects['SM_AssetFit04_Refitted_'+name];data.materials.append(old.data.materials[0])
    for f in data.polygons:f.use_smooth=True
    uv=data.uv_layers.new(name='PainterSurface')
    xs=[v.co.x for v in data.vertices];zs=[v.co.z for v in data.vertices]
    for loop in data.loops:
        co=data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=((co.x-min(xs))/max(max(xs)-min(xs),.001),(co.z-min(zs))/max(max(zs)-min(zs),.001))
    solid=c.modifiers.new('ClothThickness','SOLIDIFY');solid.thickness=.002 if name.startswith('Glove') else .006;solid.offset=-1
    c['nativeDonorHand']=name.startswith('Glove');c['ownerApproved']=False
receipt={'donor':'VRoid Base Male beta, pixiv Inc.','sourceStudy':True,'ownerApproved':False,'runtimeAdmitted':False,'coverage':[],
 'bodyVertices':len(body.data.vertices),'bodyFaces':len(body.data.polygons),'headVertices':len(face.data.vertices),'headFaces':len(face.data.polygons),
 'handMethod':'Native donor rotations evaluated before a uniform rigid hand placement; no per-finger length scaling or circular paths',
 'handTargets':hand_targets,'majorFittingFrames':frames,'newArmature':False,'retopologyGatePassed':False,'retainedCustomDesignObjects':retained}
s['anatomySourceReceipt']=json.dumps(receipt)
s.render.resolution_x=1280;s.render.resolution_y=1280
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/'
for direction,angle in [('SE',45),('W',-90),('NW',-135),('N',-180),('S',0)]:
    root.rotation_euler.z=math.radians(angle);s.render.filepath=out+direction+'-new-base-large.png';bpy.ops.render.render(write_still=True)
root.rotation_euler.z=math.radians(45);s.render.resolution_x=320;s.render.resolution_y=320
print('NEW_ANATOMY_SOURCE_STUDY '+s['anatomySourceReceipt'])
