"""Static fitting study from licensed FBX anatomy, not a rigging handoff.

Existing donor skin weights interpolate source-local rest geometry transforms.
No new armature, action, runtime character or owner approval is created here.
"""
import bpy,math,json
from mathutils import Vector,Matrix

source=bpy.data.scenes['ASTRAEON_SOURCE_LOOKDEV_03']
donor=bpy.data.scenes['ASTRAEON_FREE_FBX_INSPECTION']
outfit_source=bpy.data.scenes['ASTRAEON_FREE_OUTFIT_INSPECTION']
assert bpy.context.scene.name in {source.name,donor.name,outfit_source.name,'ASTRAEON_ASSET_FIT_04'}
scene=bpy.data.scenes.get('ASTRAEON_ASSET_FIT_04')
if scene:
    for obj in list(scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
else:scene=bpy.data.scenes.new('ASTRAEON_ASSET_FIT_04')
bpy.context.window.scene=scene
root=bpy.data.objects.new('ROOT_AssetFit04',None);scene.collection.objects.link(root)
root.rotation_euler.z=math.radians(45)
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}
canonical=Matrix.Rotation(math.pi,4,'Z')
rig=next(o for o in donor.objects if o.type=='ARMATURE')
rest={b.name:canonical@rig.matrix_world@b.matrix_local for b in rig.data.bones}
points={b.name:(canonical@rig.matrix_world@b.head_local,canonical@rig.matrix_world@b.tail_local) for b in rig.data.bones}
targets={};scales={}

def target(name,a,b,width=1,depth=None):
    a=Vector(a);b=Vector(b);old_a,old_b=points[name]
    rotation=(old_b-old_a).rotation_difference(b-a).to_matrix().to_4x4()
    orient=rotation@rest[name];orient.translation=a
    length=(b-a).length/(old_b-old_a).length
    targets[name]=orient
    scales[name]=Matrix.Diagonal((width,length,width if depth is None else depth,1))

target('root',(0,0,0),(0,1,0))
target('pelvis',P['pelvis'],P['waist']-Vector((0,0,.095)),1.28,1.25)
target('spine_01',P['waist']-Vector((0,0,.095)),P['waist']+Vector((0,0,.073)),1.2,1.18)
target('spine_02',P['waist']+Vector((0,0,.073)),P['chest'],1.05,1.12)
target('spine_03',P['chest'],P['neck']-Vector((0,0,.032)),.98,1.10)
# Head gets a measured compact-character proportion change rather than generic
# uniform rescaling of the full body.
head_center=Vector((0,0,1.695));new_head=P['head']+Vector((-.025,-.070,.005))
head_scale=Matrix.Diagonal((2.10,1.42,1.65,1))
head_transform=Matrix.Translation(new_head)@head_scale@Matrix.Translation(-head_center)
old_a,old_b=points['Head'];head_a=head_transform@old_a;head_b=head_transform@old_b
target('neck_01',P['neck'],head_a,1.18,1.18)
targets['Head']=head_transform@rest['Head'];scales['Head']=Matrix.Identity(4)

for suffix,side in [('r','R'),('l','L')]:
    shoulder,elbow,wrist,palm,hip,knee,ankle=[P[n+'_'+side] for n in ['shoulder','elbow','wrist','palm','hip','knee','ankle']]
    target('clavicle_'+suffix,P['neck']+Vector((-.02 if side=='R' else .02,0,-.035)),shoulder,.95)
    target('upperarm_'+suffix,shoulder,elbow,.78,.95)
    target('lowerarm_'+suffix,elbow,wrist,.86,.94)
    target('thigh_'+suffix,hip,knee,1.12,1.12)
    target('calf_'+suffix,knee,ankle,1.08,1.05)
    old_foot,old_ball=points['foot_'+suffix]
    ball=ankle+Vector((0,-.12,-ankle.z+.023))
    target('foot_'+suffix,ankle,ball,1.16,1.15)
    target('ball_'+suffix,ball,ball+Vector((0,-.08,0)),1.16,1.15)
    if 'ball_leaf_'+suffix in points:target('ball_leaf_'+suffix,ball+Vector((0,-.08,0)),ball+Vector((0,-.15,0)),1.16,1.15)
    axis=(P['blade_tip']-P['guard']).normalized() if side=='R' else (wrist-elbow).normalized()
    guard=P['guard'] if side=='R' else palm+axis*.096
    across=Vector((0,1,0)).cross(axis).normalized();normal=axis.cross(across).normalized()
    center=guard-axis*.096+normal*.043
    target('hand_'+suffix,wrist,wrist.lerp(center,.85),.88,1.05)
    for digit,distance in [('index',.042),('middle',.078),('ring',.114),('pinky',.15)]:
        c=guard-axis*distance
        path=[c+.037*(across*math.cos(math.radians(a))+normal*math.sin(math.radians(a))) for a in [77,25,-35,-105,-155]]
        for i in range(1,4):target(digit+'_%02d_'%i+suffix,path[i-1],path[i],1.1,1.1)
        leaf=digit+'_04_leaf_'+suffix
        if leaf in points:target(leaf,path[3],path[4],1.1,1.1)
    c=guard-axis*.063
    path=[center-across*.038+axis*.018,c-across*.043+normal*.022,c-across*.032-normal*.011,c-across*.006-normal*.037,c+across*.005-normal*.043]
    for i in range(1,4):target('thumb_%02d_'%i+suffix,path[i-1],path[i],1.12,1.12)
    leaf='thumb_04_leaf_'+suffix
    if leaf in points:target(leaf,path[3],path[4],1.12,1.12)

transforms={name:targets[name]@scales[name]@rest[name].inverted() for name in targets}

def fitted_copy(obj,label,from_rig):
    copy=obj.copy();copy.data=obj.data.copy();copy.name=label;scene.collection.objects.link(copy)
    copy.modifiers.clear();copy.parent=root;copy.matrix_parent_inverse=Matrix.Identity(4);copy.matrix_basis=Matrix.Identity(4)
    # Donor objects may carry a parent inverse; use the observed world geometry.
    basis=canonical@obj.matrix_world
    from_rest={b.name:canonical@from_rig.matrix_world@b.matrix_local for b in from_rig.data.bones}
    mapping={n:targets[n]@scales[n]@from_rest[n].inverted() for n in transforms if n in from_rest}
    for vertex in copy.data.vertices:
        p=basis@vertex.co
        weights=[(obj.vertex_groups[g.group].name,g.weight) for g in vertex.groups if obj.vertex_groups[g.group].name in mapping and g.weight>.00001]
        total=sum(weight for name,weight in weights)
        vertex.co=sum((mapping[name]@p*(weight/total) for name,weight in weights),start=Vector((0,0,0))) if total else p
    copy.data.update();copy['sourceCreator']='Quaternius';copy['archiveLicense']='CC0-1.0';copy['staticFittingStudy']=True
    return copy

body=fitted_copy(next(o for o in donor.objects if o.name.startswith('SuperHero_Male')),'SM_AssetFit04_Body',rig)
eyes=fitted_copy(next(o for o in donor.objects if o.name.startswith('Eyes')),'SM_AssetFit04_Eyes',rig)
brows=fitted_copy(next(o for o in donor.objects if o.name.startswith('Eyebrows')),'SM_AssetFit04_Brows',rig)
# The glTF import resolved its texture paths correctly; use matching original
# UV materials on the FBX topology instead of missing external FBX path links.
gl_scene=bpy.data.scenes['ASTRAEON_FREE_BASE_INSPECTION']
for obj,prefix in [(body,'SuperHero_Male'),(eyes,'Eyes'),(brows,'Eyebrows')]:
    original=next(o for o in gl_scene.objects if o.name.startswith(prefix))
    obj.data.materials.clear()
    for material in original.data.materials:obj.data.materials.append(material)

# Compare only compatible boots/pants at this stage; the complete Ranger outfit
# changes the approved Swordsman costume and is not substituted silently.
outfit_rig=next(o for o in outfit_source.objects if o.type=='ARMATURE')
for name in ('Male_Ranger_Feet_Boots','Male_Ranger_Legs'):
    original=next(o for o in outfit_source.objects if o.name==name)
    obj=fitted_copy(original,'SM_AssetFit04_'+name,outfit_rig)
    obj.hide_render=True;obj['inspectionOnly']=True

# Use the fresh original source's editable costume for one fair fitting view.
# Exclude the old voxel anatomy, modeled face and extracted limb clothing.
for obj in source.objects:
    if obj.type!='MESH':continue
    if obj.name=='Body_VolumeBlockout' or obj.name in bpy.data.collections['HEAD_FEATURES'].objects:continue
    clone=obj.copy();clone.data=obj.data.copy();clone.name='SM_AssetFit04_'+obj.name
    scene.collection.objects.link(clone);clone.parent=root
    clone['sourceOrigin']='Original fresh ASTRAEON costume study';clone['ownerApproved']=False
    # Source-native outfit needs refitting to this different anatomical surface.
    if obj.name.startswith('Fitted_') and not obj.name.startswith('Fitted_Bracer_'):
        clone.hide_render=True;clone['inspectionOnly']=True

for obj in source.objects:
    if obj.type in ('CAMERA','LIGHT'):
        clone=obj.copy();clone.data=obj.data.copy();scene.collection.objects.link(clone)
        if obj.type=='CAMERA':scene.camera=clone
scene.world=source.world
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=320;scene.render.resolution_y=320;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='Standard'
scene['status']='STATIC_LICENSED_ANATOMY_FIT_NOT_RIGGING_HANDOFF';scene['ownerApproved']=False;scene['runtimeAdmitted']=False
scene['fitTransforms']=json.dumps({n:[list(row) for row in m] for n,m in transforms.items()})
scene['targetRestFrames']=json.dumps({n:[list(row) for row in m] for n,m in targets.items()})
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/asset-fit-04'
scene.render.resolution_x=1280;scene.render.resolution_y=1280
scene.render.filepath=out+'/renders/SE-initial-fit.png';bpy.ops.render.render(write_still=True)
scene.render.resolution_x=320;scene.render.resolution_y=320
print('STATIC_ASSET_FIT_COMPLETE',len(scene.objects),'NO_NEW_ARMATURE_NO_ACTION_COVERAGE')
