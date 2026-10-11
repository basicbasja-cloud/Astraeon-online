"""Transfer sampled CC0 motions to the fitted fantasy rig with a neutral wrist.

World-space rest/pose rotation differences correct differing bone rolls and
proportions. Donor meshes, weights, cameras, and finger poses are never copied.
The right wrist stays neutral and the hilt remains perpendicular to the forearm.
"""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Matrix, Quaternion, Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'authoring/characters/swordsman-production/fantasy-base-01'
s=bpy.context.scene;rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']]
root.rotation_euler.z=0
samples=json.loads((OUT/'factory/free-motion-samples.json').read_text())['clips']
clips=json.loads(s['clips'])
mapping={'Hips':'pelvis','Spine':'spine_01','Chest':'spine_03','Neck':'neck_01','Head':'Head'}
for side,ss in [('R','r'),('L','l')]:
    for target,source in [('Clavicle','clavicle'),('UpperArm','upperarm'),('Forearm','lowerarm'),
                          ('Hand','hand'),('Thigh','thigh'),('Shin','calf'),('Foot','foot'),('Toe','ball')]:
        mapping[target+'.'+side]=source+'_'+ss
mapping.pop('Hand.R')  # Anatomical wrist alignment and custom gripping fingers win.
# Continuous cloth contacts the floor after skinning. This is native source
# geometry deformation, shared by composite/independent layers and every view.
group=bpy.data.node_groups.get('F01_CapeFloorContact')
if group is None:
    group=bpy.data.node_groups.new('F01_CapeFloorContact','GeometryNodeTree')
    group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    nodes=group.nodes;links=group.links;input=nodes.new('NodeGroupInput');output=nodes.new('NodeGroupOutput')
    position=nodes.new('GeometryNodeInputPosition');split=nodes.new('ShaderNodeSeparateXYZ');combine=nodes.new('ShaderNodeCombineXYZ')
    maximum=nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM';maximum.inputs[1].default_value=.004
    setpos=nodes.new('GeometryNodeSetPosition')
    links.new(position.outputs['Position'],split.inputs[0]);links.new(split.outputs['X'],combine.inputs['X']);links.new(split.outputs['Y'],combine.inputs['Y'])
    links.new(split.outputs['Z'],maximum.inputs[0]);links.new(maximum.outputs[0],combine.inputs['Z'])
    links.new(input.outputs['Geometry'],setpos.inputs['Geometry']);links.new(combine.outputs[0],setpos.inputs['Position']);links.new(setpos.outputs['Geometry'],output.inputs['Geometry'])
for o in s.objects:
    if o.type=='MESH' and o.get('spriteModule')=='Cape' and not o.hide_render:
        mod=o.modifiers.get('ClothFloorContact') or o.modifiers.new('ClothFloorContact','NODES');mod.node_group=group
contact=json.loads(s['swordContact']);center=Vector(contact['centerModel']);old=Vector(contact['axisModel'])
forearm=(rig.data.bones['Forearm.R'].tail_local-rig.data.bones['Forearm.R'].head_local).normalized()
axis=(old-forearm*old.dot(forearm)).normalized();correction=old.rotation_difference(axis)
for o in s.objects:
    if o.get('spriteModule')=='Weapon':
        for v in o.data.vertices:v.co=center+correction@(v.co-center)
        o.data.update()
contact['axisModel']=list(axis);s['swordContact']=json.dumps(contact)
s['restingHandQuaternion']=json.dumps([1,0,0,0]);s['gripAlignment']='90 degree sword/forearm; neutral right wrist, owner confirmed.'
for a in list(bpy.data.actions):
    if a.name.startswith('F01_'):bpy.data.actions.remove(a)
rig.animation_data_clear()
for side in ['R','L']:
    p=rig.pose.bones['Foot.'+side]
    for c in list(p.constraints):
        if c.name.startswith('GroundOrientation'):p.constraints.remove(c)
def reset():
    for p in rig.pose.bones:p.rotation_mode='QUATERNION';p.rotation_quaternion=Quaternion();p.location=(0,0,0);p.scale=(1,1,1)
    for side in ['R','L']:rig.pose.bones['Shin.'+side].constraints['GroundContactIK'].influence=0
def turn(name,axis,angle):
    p=rig.pose.bones[name];local=p.bone.matrix_local.to_3x3().inverted()@Vector(axis)
    p.rotation_quaternion=p.rotation_quaternion@Quaternion(local.normalized(),math.radians(angle))
def shift(name,delta):rig.pose.bones[name].location=rig.data.bones[name].matrix_local.to_3x3().inverted()@Vector(delta)
gripTwist=None
evidence=[]
for clip in clips:
    name=clip['name'];data=samples[name];rest={n:Matrix(b['matrix']).to_quaternion() for n,b in data['rest'].items()}
    sourceHip=Vector(data['rest']['pelvis']['head']);legScale=(rig.data.bones['Hips'].head_local.z-rig.data.bones['Foot.R'].head_local.z)/(sourceHip.z-Vector(data['rest']['foot_r']['head']).z)
    action=bpy.data.actions.new('F01_'+name);action.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=action
    floorCorrections=[];angles=[]
    for f,frame in enumerate(data['frames'],1):
        reset();t=frame['t'];desired={}
        for target,source in mapping.items():
            donor=Matrix(frame['bones'][source]['matrix']).to_quaternion()
            desired[target]=(donor@rest[source].inverted())@rig.data.bones[target].matrix_local.to_quaternion()
        # Parent-before-child traversal preserves local joint rotations, not donor lengths.
        for p in rig.pose.bones:
            if p.name not in desired:continue
            parent=p.parent
            if parent:
                if parent.name in desired:parentPose=desired[parent.name]
                else:parentPose=parent.bone.matrix_local.to_quaternion()
                inherited=parentPose@parent.bone.matrix_local.to_quaternion().inverted()@p.bone.matrix_local.to_quaternion()
            else:inherited=p.bone.matrix_local.to_quaternion()
            p.rotation_quaternion=inherited.inverted()@desired[p.name]
        displacement=(Vector(frame['bones']['pelvis']['head'])-sourceHip)*legScale
        shift('Hips',displacement)
        # Enforce the owner's grip on every pose, including attacks and death.
        rig.pose.bones['Hand.R'].rotation_quaternion=Quaternion()
        for side in ['R','L']:
            for digit in ['Index','Middle','Ring','Pinky']:
                for j,angle in enumerate([45,85,70] if side=='R' else [15,18,12],1):
                    rig.pose.bones[digit+str(j)+'.'+side].rotation_quaternion=Quaternion((1,0,0),math.radians(-angle))
            if side=='R':
                for j,angle in enumerate([12,32,40],1):rig.pose.bones['Thumb'+str(j)+'.R'].rotation_quaternion=Quaternion((1,0,0),math.radians(-angle))
        turn('Head',(1,0,0),-20)
        bpy.context.view_layer.update()
        # Calibrate one forearm pronation offset from the neutral donor pose.
        # Rotate around the actual forearm long axis, never bend the wrist to
        # make the blade point outward. Apply the same offset to every clip.
        fore=rig.pose.bones['Forearm.R'];hp=rig.pose.bones['Hand.R']
        if gripTwist is None:
            longitudinal=(fore.tail-fore.head).normalized()
            current=((hp.matrix@hp.bone.matrix_local.inverted()).to_3x3()@axis).normalized()
            wanted=Vector((-.45,-1,-.15));wanted=(wanted-longitudinal*wanted.dot(longitudinal)).normalized()
            gripTwist=math.atan2(longitudinal.dot(current.cross(wanted)),current.dot(wanted))
        fore.rotation_quaternion=fore.rotation_quaternion@Quaternion((0,1,0),gripTwist)
        # Delayed source-space cape overlap; one pose serves all eight headings.
        amount={'Walk':6,'Run':12,'Sprint':18,'Dash':20,'BasicAttack':9,'SkillAction':12}.get(name,0)
        for j,base in enumerate([12,8,6]):
            turn('Cape'+str(j),(1,0,0),base+amount*(.65+.35*math.sin(math.tau*t-j*.75))+1.2*math.sin(math.tau*t-j*.6))
        bpy.context.view_layer.update()
        low=1e6;dg=bpy.context.evaluated_depsgraph_get()
        for o in [bpy.data.objects['F01_BodyOutfit'],bpy.data.objects['F01_HeadHair']]:
            evaluated=o.evaluated_get(dg);mesh=evaluated.to_mesh()
            low=min(low,min(v.co.z for v in mesh.vertices));evaluated.to_mesh_clear()
        # Keep the real deformed soles on the floor, retaining donor step lift/bob.
        correctionZ=max(0,-low)
        if name in ['Idle','Walk','Run','Sprint','Guard','BasicAttack','SkillAction']:correctionZ=-low
        shift('Hips',displacement+Vector((0,0,correctionZ)));floorCorrections.append(correctionZ)
        bpy.context.view_layer.update()
        hand=rig.pose.bones['Hand.R'];deform=hand.matrix@hand.bone.matrix_local.inverted()
        weaponAxis=(deform.to_3x3()@axis).normalized();forearmAxis=(rig.pose.bones['Forearm.R'].tail-rig.pose.bones['Forearm.R'].head).normalized()
        angle=math.degrees(weaponAxis.angle(forearmAxis));angles.append(angle)
        assert abs(angle-90)<.05, (name,f,angle)
        for p in rig.pose.bones:
            p.keyframe_insert(data_path='rotation_quaternion',frame=f,group=p.name)
            if p.name=='Hips' or p.name.startswith('CTRL_'):p.keyframe_insert(data_path='location',frame=f,group=p.name)
        for side in ['R','L']:rig.pose.bones['Shin.'+side].constraints['GroundContactIK'].keyframe_insert(data_path='influence',frame=f)
    evidence.append({'action':name,'sourcePack':data['pack'],'sourceActions':data['sourceActions'],'fileSHA256':data['fileSHA256'],
                     'retargetedFrames':len(data['frames']),'legScale':legScale,'floorCorrectionRange':[min(floorCorrections),max(floorCorrections)],
                     'gripForearmDegreesRange':[min(angles),max(angles)],'forearmPronationOffsetDegrees':math.degrees(gripTwist),
                     'neutralWrist':True,'visualAccepted':False})
    print('FREE_MOTION_RETARGETED '+name,flush=True)
s['motionStatus']='CC0_RETARGETED_AND_GRIP_CORRECTED_REQUIRES_VISUAL_REVIEW'
s['freeMotionEvidence']=json.dumps(evidence);s['ownerApproved']=False;s['runtimeAdmitted']=False
rig.animation_data.action=bpy.data.actions['F01_Idle'];s.frame_start=1;s.frame_end=8;s.frame_set(1);root.rotation_euler.z=math.radians(45)
s.render.resolution_x=320;s.render.resolution_y=320
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'.character-tools/checkpoints/fantasy-base-01-native.blend'))
(OUT/'factory/motion-retarget.json').write_text(json.dumps({'actions':evidence,'noDonorGeometry':True,'wristInterpretation':'Owner confirmed perpendicular sword/grip and naturally aligned wrist.',
    'motionSamplesSHA256':hashlib.sha256((OUT/'factory/free-motion-samples.json').read_bytes()).hexdigest(),'ownerApproved':False},indent=2)+'\n')
