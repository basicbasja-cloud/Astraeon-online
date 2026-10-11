"""Author sampled, editable motions on the fitted source with planted-foot IK.

Uses the project's action timing contract. No drivers, handlers, bone scaling,
image cards, mirrored headings, or view-specific pose corrections.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion

base=Path(__file__).resolve().parents[1];s=bpy.context.scene
rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']]
root.rotation_euler.z=0
blueprint=json.loads((base/'authoring/characters/true-modular/swordsman/male/blueprint.json').read_text(encoding='utf-8-sig'))
matrix=json.loads((base/'docs/character-factory/new-production-matrix.json').read_text())
hand=Quaternion(json.loads(s['restingHandQuaternion']))
for a in list(bpy.data.actions):
    if a.name.startswith('F01_'):bpy.data.actions.remove(a)
rig.animation_data_clear()
def reset():
    for p in rig.pose.bones:p.rotation_quaternion=Quaternion();p.location=(0,0,0);p.scale=(1,1,1)
def turn(name,axis,angle):
    p=rig.pose.bones[name];local=p.bone.matrix_local.to_3x3().inverted()@Vector(axis)
    p.rotation_quaternion=p.rotation_quaternion@Quaternion(local.normalized(),math.radians(angle))
def shift(name,delta):
    p=rig.pose.bones[name];p.location=p.bone.matrix_local.to_3x3().inverted()@Vector(delta)
def target(side,xyz):
    p=rig.pose.bones['CTRL_Foot.'+side];desired=Vector(xyz);desired.y+=s.get('originShiftY',0);shift(p.name,desired-p.bone.head_local)
copy_constraints={}
for side in ['R','L']:
    p=rig.pose.bones['Foot.'+side]
    c=p.constraints.new('COPY_ROTATION');c.name='GroundOrientation';c.target=rig;c.subtarget='CTRL_Foot.'+side;c.owner_space='POSE';c.target_space='POSE'
    copy_constraints[side]=c
# Calibrate poles against the actual fitted bind, rather than guess a rig roll.
reset();bpy.context.view_layer.update();poles={}
for side in ['R','L']:
    c=rig.pose.bones['Shin.'+side].constraints['GroundContactIK'];c.influence=1
    candidates=[]
    for angle in [0,90,-90,180]:
        c.pole_angle=math.radians(angle);bpy.context.view_layer.update()
        error=(rig.pose.bones['Shin.'+side].head-rig.data.bones['Shin.'+side].head_local).length
        candidates.append((error,angle))
    error,angle=min(candidates);c.pole_angle=math.radians(angle);poles[side]={'poleAngleDegrees':angle,'bindKneeError':error}
def smooth(t):return t*t*(3-2*t)
def idle(t):
    reset();pulse=math.sin(math.tau*t)
    for side,sign in [('R',-1),('L',1)]:
        rig.pose.bones['Shin.'+side].constraints['GroundContactIK'].influence=1;copy_constraints[side].influence=1
        target(side,(sign*.087,.034,.075))
        turn('UpperArm.'+side,(0,1,0),sign*69)
        turn('Forearm.'+side,(0,1,0),-sign*8)
        for digit in ['Index','Middle','Ring','Pinky']:
            for j,angle in enumerate([45,85,70] if side=='R' else [15,18,12],1):rig.pose.bones[digit+str(j)+'.'+side].rotation_quaternion=Quaternion((1,0,0),math.radians(-angle))
        if side=='R':
            for j,angle in enumerate([12,32,40],1):rig.pose.bones['Thumb'+str(j)+'.R'].rotation_quaternion=Quaternion((1,0,0),math.radians(-angle))
    rig.pose.bones['Hand.R'].rotation_quaternion=hand.copy()
    turn('Chest',(1,0,0),.6*pulse)
    turn('Head',(1,0,0),-12)
    for j,angle in enumerate([12,8,6]):turn('Cape'+str(j),(1,0,0),angle+1.3*math.sin(math.tau*t-j*.6))
def pose(action,t):
    idle(t);pulse=math.sin(math.tau*t);peak=math.sin(math.pi*t)
    if action in ['Walk','Run','Sprint','Dash']:
        stride,lift,drop,lean={'Walk':(.13,.025,.022,3),'Run':(.22,.052,.033,8),'Sprint':(.27,.065,.043,12),'Dash':(.24,.042,.04,15)}[action]
        gate=1 if action!='Dash' else peak
        shift('Hips',(0,0,-drop*gate+.003*math.cos(math.tau*t*2)*gate))
        turn('Chest',(1,0,0),lean*gate)
        for side,sign,offset in [('R',-1,0),('L',1,.5)]:
            phase=(t+offset)%1
            if phase<.55:yy=-stride/2+stride*phase/.55;zz=0;pitch=0
            else:
                q=(phase-.55)/.45;yy=stride/2-stride*smooth(q);zz=lift*math.sin(math.pi*q);pitch=-10*math.sin(math.pi*q)
            target(side,(sign*.087,.034+yy*gate,.075+zz*gate))
            turn('CTRL_Foot.'+side,(1,0,0),pitch*gate)
            turn('UpperArm.'+side,(0,0,1),-sign*math.sin(math.tau*(t+offset))*18*gate)
        turn('Cape0',(1,0,0),(6 if action=='Walk' else 12)*gate)
    elif action in ['BasicAttack','SkillAction']:
        if t<.26:q=smooth(t/.26);lift=135*q;twist=-28*q
        elif t<.57:q=smooth((t-.26)/.31);lift=135-153*q;twist=-28+63*q
        else:q=smooth((t-.57)/.43);lift=-18*(1-q);twist=35*(1-q)
        turn('UpperArm.R',(0,1,0),lift)
        turn('UpperArm.R',(0,0,1),peak*35)
        turn('Forearm.R',(0,0,1),peak*30)
        turn('Chest',(0,0,1),twist)
        turn('UpperArm.L',(0,0,1),-peak*38)
        shift('Hips',(0,0,-.025*peak))
        if action=='SkillAction':turn('Chest',(1,0,0),15*peak)
    elif action in ['Guard','CastChannel','CastRelease']:
        q=1 if action!='CastRelease' else 1-smooth(t)
        turn('UpperArm.R',(0,0,1),50*q);turn('Forearm.R',(0,0,1),40*q)
        turn('UpperArm.L',(0,0,1),-55*q);turn('Forearm.L',(0,0,1),-60*q)
        shift('Hips',(0,0,-.014*q));turn('Chest',(1,0,0),4*q)
    elif action=='Hit':
        turn('Chest',(1,0,0),-18*peak);turn('Head',(1,0,0),-7*peak);shift('Hips',(0,.018*peak,-.018*peak))
    elif action in ['Interact','ItemUse']:
        turn('UpperArm.L',(0,0,1),-70*peak);turn('Forearm.L',(0,0,1),-55*peak)
        if action=='ItemUse':turn('Head',(0,0,1),8*peak)
    elif action=='Pickup':
        shift('Hips',(0,0,-.09*peak));turn('Chest',(1,0,0),38*peak);turn('UpperArm.L',(0,0,1),-50*peak)
    elif action=='Sit':
        shift('Hips',(0,.045,-.285));turn('Chest',(1,0,0),8)
        for side,sign in [('R',-1),('L',1)]:target(side,(sign*.12,-.13,.075))
    elif action in ['Death','Respawn']:
        q=smooth(t) if action=='Death' else 1-smooth(t)
        for side in ['R','L']:
            rig.pose.bones['Shin.'+side].constraints['GroundContactIK'].influence=1-q;copy_constraints[side].influence=1-q
        turn('Hips',(1,0,0),86*q);shift('Hips',(0,.055*q,-.355*q))
        turn('UpperArm.L',(0,0,1),-20*q);turn('UpperArm.R',(0,0,1),30*q)
        turn('Head',(0,0,1),18*q)
    bpy.context.view_layer.update()
    # Remove only actual floor penetration, with a shared rig-space correction.
    # Ground correction is evaluated from the deformed boot/body, never a view.
    body=bpy.data.objects['F01_BodyOutfit'];dg=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(dg)
    me=evaluated.to_mesh();low=min(v.co.z for v in me.vertices);evaluated.to_mesh_clear()
    if low<-.0005:
        current=rig.pose.bones['Hips'].location.copy()
        shift('Hips',rig.data.bones['Hips'].matrix_local.to_3x3()@current+Vector((0,0,-low)))
        bpy.context.view_layer.update()
clips=[]
for entry in matrix['actions']:
    name=entry['action']
    if entry['swordsmanContract']=='excluded':continue
    timing=blueprint['clips'][name];count=timing['frames'];loop=timing['loop']
    a=bpy.data.actions.new('F01_'+name);a.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=a
    for f in range(count+(1 if loop else 0)):
        pose(name,f/count if loop else f/(count-1))
        for p in rig.pose.bones:
            p.keyframe_insert(data_path='rotation_quaternion',frame=f+1,group=p.name)
            if p.name=='Hips' or p.name.startswith('CTRL_'):p.keyframe_insert(data_path='location',frame=f+1,group=p.name)
        for side in ['R','L']:
            rig.pose.bones['Shin.'+side].constraints['GroundContactIK'].keyframe_insert(data_path='influence',frame=f+1)
            copy_constraints[side].keyframe_insert(data_path='influence',frame=f+1)
    clips.append({'name':name,'action':a.name,'frames':count,'loop':loop,'durationsMs':timing['durationsMs'],'contract':entry['swordsmanContract'],'ownerApproved':False})
s['clips']=json.dumps(clips);s['motionStatus']='AUTHORED_WITH_IK_REQUIRES_VISUAL_REVIEW';s['poleCalibration']=json.dumps(poles)
rig.animation_data.action=bpy.data.actions['F01_Idle'];s.frame_start=1;s.frame_end=8;s.frame_set(1);root.rotation_euler.z=math.radians(45)
s.render.resolution_x=320;s.render.resolution_y=320
bpy.ops.wm.save_as_mainfile(filepath=str(base/'.character-tools/checkpoints/fantasy-base-01-native.blend'))
(base/'authoring/characters/swordsman-production/fantasy-base-01/clips.json').write_text(json.dumps({'clips':clips,'poleCalibration':poles,'ownerApproved':False},indent=2)+'\n')
for action in ['Idle','Walk','BasicAttack','Death']:
    clip=next(c for c in clips if c['name']==action);rig.animation_data.action=bpy.data.actions[clip['action']]
    for f in sorted(set([1,clip['frames']//2+1,clip['frames']])):
        s.frame_set(f)
        for direction,yaw in [('SE',45),('W',-90),('NW',-135),('N',-180)]:
            root.rotation_euler.z=math.radians(yaw);s.render.resolution_x=640;s.render.resolution_y=640
            s.render.filepath=str(base/'authoring/characters/swordsman-production/fantasy-base-01/renders'/(action+'-'+direction+'-'+str(f).zfill(2)+'.png'));bpy.ops.render.render(write_still=True)
print('FANTASY_MOTIONS_AUTHORED '+json.dumps({'actions':len(clips),'requiredPositions':8*sum(c['frames'] for c in clips if c['contract']=='required'),'poles':poles}),flush=True)
