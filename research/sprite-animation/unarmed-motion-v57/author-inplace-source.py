"""Original in-place RPG adaptation of fresh CC0 unarmed angles.

Retains external upper-body timing/rotations and vertical pelvis motion. Locks
planar pelvis/feet to the source guard stance and solves original-length legs.
The external forward lunge is deliberately excluded before any sprite rendering.
"""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector,Quaternion,Matrix
P=Path(__file__).resolve().parent;source=P/'source/cc0-motion.json';D=json.loads(source.read_text());blend=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update();rig=bpy.data.objects['Astraeon_Free_Local'];world=rig.matrix_world.copy();inv=world.inverted();neutral={n:{'matrix':world@b.matrix.copy(),'head':world@b.head,'tail':world@b.tail} for n,b in rig.pose.bones.items()}
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH' and o.data.shape_keys and o.data.shape_keys.animation_data:o.data.shape_keys.animation_data_clear()
for b in rig.pose.bones:
 for c in b.constraints:c.mute=True
 b.rotation_mode='QUATERNION'
gem=bpy.data.objects['collectible'];gem.hide_render=True
def setbone(n,head,q):
 b=rig.pose.bones[n];scale=neutral[n]['matrix'].to_scale();b.matrix=inv@Matrix.LocRotScale(head,q,scale);bpy.context.view_layer.update()
for n,a in neutral.items():rig.pose.bones[n].matrix=inv@a['matrix'];bpy.context.view_layer.update()
G=D['neutral_general_idle']['bones'];guard=D['clips']['Melee_Unarmed_Idle']['frames'][0]['bones']
def vec(b,edge='head'):return Vector(b[edge])
def pelvis(b):return (vec(b['upperleg.l'])+vec(b['upperleg.r']))/2
def nq(n):return neutral[n]['matrix'].to_quaternion()
def delta(b,n):return Quaternion(b[n]['rotation_wxyz'])@Quaternion(G[n]['rotation_wxyz']).inverted()
arm_roll={}
for side,suffix in [('left','l'),('right','r')]:
 for target,bone in [('upperarm','upperarm'),('forearm','lowerarm'),('hand','hand')]:
  n=side+'.'+target;src=bone+'.'+suffix;before=neutral[n]['tail']-neutral[n]['head'];after=vec(G[src],'tail')-vec(G[src]);aim=before.rotation_difference(after)@nq(n);arm_roll[n]=Quaternion(G[src]['rotation_wxyz']).inverted()@aim
def armq(b,side,target,bone,suffix):return Quaternion(b[bone+'.'+suffix]['rotation_wxyz'])@arm_roll[side+'.'+target]
target_span=sum(neutral[s+'.upperarm']['head'].z-neutral[s+'.foot']['head'].z for s in ['left','right'])/2;source_span=sum(vec(G['upperarm.'+s]).z-vec(G['foot.'+s]).z for s in ['l','r'])/2;gain=target_span/source_span;hip0=neutral['torso']['head'];gp=pelvis(G);guardp=pelvis(guard);planar=Vector((0,0,0));feet={side:neutral[side+'.foot']['head'].copy() for side in ['left','right']}
for side in feet:feet[side].z=neutral[side+'.foot']['head'].z
# A single source-only pelvis clearance, computed before baking, keeps original
# bone lengths reachable through the whole external clip. No raster feedback.
required_dip=.02
for clip in D['clips'].values():
 for row in clip['frames']:
  b=row['bones'];hq=delta(b,'hips');h=hip0.copy();h.z+=(pelvis(b).z-guardp.z)*gain
  for side in ['left','right']:
   t=side+'.thigh';k=side+'.shin';joint=h+hq@(neutral[t]['head']-hip0);foot=feet[side];length=(neutral[t]['tail']-neutral[t]['head']).length+(neutral[k]['tail']-neutral[k]['head']).length;rho=(joint.x-foot.x)**2+(joint.y-foot.y)**2
   if rho>=length*length:raise ValueError('Unreachable planar stance')
   required_dip=max(required_dip,joint.z-foot.z-math.sqrt(length*length-rho)+.005)
guard_dip=math.ceil(required_dip*1000)/1000
print('SOURCE_ONLY_CONSTANT_GUARD_DIP',guard_dip,flush=True)

def ik(h,a,l1,l2,pole):
 axis=a-h;distance=axis.length
 if not 1e-5<distance<l1+l2-1e-7:raise ValueError(('unreachable_fixed_foot',distance,l1+l2))
 axis.normalize();u=pole-axis*pole.dot(axis)
 if u.length<1e-6:raise ValueError('ambiguous_knee_pole')
 u.normalize();along=(l1*l1-l2*l2+distance*distance)/(2*distance);height=math.sqrt(max(0,l1*l1-along*along));return h+axis*along+u*height
def orient(n,a,b):
 before=neutral[n]['tail']-neutral[n]['head'];after=b-a;return before.rotation_difference(after)@nq(n)
actions={};maxerr=0;maxfoot=0;times=[]
for key,clipname,duration in [('ready','Melee_Unarmed_Idle',1070),('attack1','Melee_Unarmed_Attack_Punch_A',1170)]:
 action=bpy.data.actions.new('Original_'+key+'_CC0_inplace');action.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=action;action['duration_ms']=duration;action['phase_frame_start']=1;action['phase_frame_end']=257;frames=D['clips'][clipname]['frames'];lastq={}
 for i,row in enumerate(frames):
  sc.frame_set(1+i);b=row['bones'];hip=hip0+planar;hip.z+=(pelvis(b).z-guardp.z)*gain-guard_dip;torso_delta=delta(b,'chest');hip_delta=delta(b,'hips');setbone('root',neutral['root']['head'],nq('root'));setbone('torso',hip,torso_delta@nq('torso'));head=hip+torso_delta@(neutral['head']['head']-hip0);setbone('head',head,delta(b,'head')@nq('head'))
  for side,s in [('left','l'),('right','r')]:
   upper=side+'.upperarm';fore=side+'.forearm';hand=side+'.hand';shoulder=hip+torso_delta@(neutral[upper]['head']-hip0);l1=(neutral[upper]['tail']-neutral[upper]['head']).length;l2=(neutral[fore]['tail']-neutral[fore]['head']).length
   su=vec(b['upperarm.'+s]);se=vec(b['lowerarm.'+s]);sw=vec(b['hand.'+s]);source_length=max((vec(r['bones']['lowerarm.'+s])-vec(r['bones']['upperarm.'+s])).length+(vec(r['bones']['hand.'+s])-vec(r['bones']['lowerarm.'+s])).length for clip in D['clips'].values() for r in clip['frames']);wrist=shoulder+(sw-su)*((l1+l2-.001)/source_length);elbow=ik(shoulder,wrist,l1,l2,se-su);uq=orient(upper,shoulder,elbow);fq=orient(fore,elbow,wrist);hq=fq@nq(fore).inverted()@nq(hand);setbone(upper,shoulder,uq);setbone(fore,elbow,fq);setbone(hand,wrist,hq)
   thigh=side+'.thigh';shin=side+'.shin';foot=side+'.foot';h=hip+hip_delta@(neutral[thigh]['head']-hip0);l1=(neutral[thigh]['tail']-neutral[thigh]['head']).length;l2=(neutral[shin]['tail']-neutral[shin]['head']).length;knee=ik(h,feet[side],l1,l2,hip_delta@Vector((0,-1,0)));setbone(thigh,h,orient(thigh,h,knee));setbone(shin,knee,orient(shin,knee,feet[side]));setbone(foot,feet[side],nq(foot))
  bpy.context.view_layer.update();gem.hide_render=True
  for n,p in rig.pose.bones.items():
   if n in lastq and p.rotation_quaternion.dot(lastq[n])<0:p.rotation_quaternion.negate()
   lastq[n]=p.rotation_quaternion.copy()
   for path in ['location','rotation_quaternion','scale']:p.keyframe_insert(data_path=path,frame=i+1,group=n)
  for side in ['left','right']:maxerr=max(maxerr,((world@rig.pose.bones[side+'.foot'].head)-feet[side]).length)
 for f in action.fcurves:
  for k in f.keyframe_points:k.interpolation='LINEAR'
 actions[key]={'action':action.name,'source_clip':clipname,'duration_ms':duration,'source_duration_seconds':D['clips'][clipname]['duration_seconds'],'source_samples':257,'frame_range':[1,257]};print('BAKED',key,flush=True)
rig.animation_data.action=bpy.data.actions[actions['ready']['action']];sc.frame_set(1);sc.frame_start=1;sc.frame_end=257;sc.render.fps=240;dest=P/'source/unarmed-inplace.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest));report={'parent_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'external_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_coordinate_frame':'BlenderZup, anatomicalLEFT+X, forward-Y for both rigs; no mirroring','global_translation_gain_from_shoulder_to_ankle_height':gain,'fixed_guard_feet_world':{n:list(v) for n,v in feet.items()},'planar_guard_hip_offset':list(planar),'constant_guard_dip_m':guard_dip,'guard_dip_policy':'Single whole-clip source-only original-length IK reachability clearance, roundedup1mm plus5mm knee margin; never raster/per-frame fitting','actions':actions,'max_actual_sampled_ankle_target_error_m':maxerr,'neutral_bones':{n:{'head':list(a['head']),'tail':list(a['tail']),'rotation_wxyz':list(a['matrix'].to_quaternion())} for n,a in neutral.items()},'arm_calibration':'Actual CC0 wrist relative to current source shoulder, one whole-arm length gain, original target upper/forearm lengths solved by IK with actual current CC0 elbow plane. Wrist stays aligned to forearm in original neutral hand relation for a closed fist; external wrist roll is excluded.', 'adaptation':'Authored in-place attack: preserve CC0 upper-body world-angle deltas and vertical pelvis motion; lock feet/orientation and planar pelvis to original neutral stance, author one source-only constant guard clearance, retain CC0 pelvisZ motion relative to guard0, analytic original-length leg IK. External full lunge/foot roll is not copied. This is not an exact external clip replay.','clock':'Blender1..257 is normalized phase; per-action duration_ms controls playback. No257newdrawings.','production_pass':False};(P/'source/authoring-receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('AUTHORING_ERROR',maxerr,flush=True)
