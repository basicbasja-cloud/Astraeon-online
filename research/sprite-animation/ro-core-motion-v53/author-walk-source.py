"""Original source walk on read-only saved body. Source/guide proof, never painted art approval."""
from pathlib import Path
import bpy,math,json,hashlib,sys
from mathutils import Vector as V,Matrix
P=Path(__file__).resolve().parent;parent=P.parent/'pickup-sixteen-v48/source/parent-v45.blend'
bpy.ops.wm.open_mainfile(filepath=str(parent));sc=bpy.context.scene;rig=bpy.data.objects['Astraeon_Free_Local'];rig.animation_data_clear();bpy.data.objects['collectible'].animation_data_clear();bpy.data.objects['collectible'].hide_render=True
BM={b.name:b.matrix_local.copy() for b in rig.data.bones};parents={b.name:b.parent.name if b.parent else None for b in rig.data.bones};resthip=BM['root'].translation.copy();sole={s:[o.matrix_world@v.co for v in o.data.vertices] for s in ['left','right'] for o in [bpy.data.objects[s+'.sole']]}
def foot_path(p):
 p%=1;stride=.32;stance=.6;front=-stride/3
 if p<stance:return front+stride*p,0
 q=(p-stance)/(1-stance);m=stride*(1-stance);start=front+stride*stance
 y=(2*q**3-3*q*q+1)*start+(q**3-2*q*q+q)*m+(-2*q**3+3*q*q)*front+(q**3-q*q)*m
 return y,.06*math.sin(math.pi*q)**2
def ik(a,b,l1,l2,pole):
 n=b-a;distance=n.length
 if not abs(l1-l2)+1e-7<distance<l1+l2-1e-7:raise ValueError(('unreachable',distance,l1+l2))
 n.normalize();v=pole-a;v-=n*v.dot(n);v.normalize();along=(l1*l1-l2*l2+distance*distance)/(2*distance)
 return a+n*along+v*math.sqrt(max(0,l1*l1-along*along))
def hinge(y,n):
 y=y.normalized();n=n.normalized();x=y.cross(n).normalized();z=x.cross(y).normalized();return Matrix((x,y,z)).transposed().to_quaternion()
def pose(u):
 # Local root remains in place; world movement is -stride*u along Y.
 hip=resthip+V((.006*math.sin(2*math.pi*u),0,-.012+.008*math.cos(4*math.pi*u)));T=Matrix.Translation(hip);inv=Matrix.Translation(-resthip)
 root=T@Matrix.Rotation(math.radians(1.5)*math.sin(2*math.pi*u),4,'Z')@inv;torso=T@Matrix.Rotation(math.radians(-3)*math.sin(2*math.pi*u),4,'Z')@inv
 desired={'root':root@BM['root'],'torso':torso@BM['torso'],'head':torso@BM['head']};metadata={}
 for side,offset in [('left',0),('right',.5)]:
  phase=(u+offset)%1;y,lift=foot_path(phase);foot=BM[side+'.foot'].copy();foot.translation=V((foot.translation.x,y,foot.translation.z+lift));low=min((foot@BM[side+'.foot'].inverted()@v).z for v in sole[side]);foot.translation.z+=lift-low
  h=root@BM[side+'.thigh'].translation;a=foot.translation;l1=(BM[side+'.shin'].translation-BM[side+'.thigh'].translation).length;l2=(BM[side+'.foot'].translation-BM[side+'.shin'].translation).length;k=ik(h,a,l1,l2,h+V((0,-1,-.4)));upper=(k-h).normalized();lower=(a-k).normalized();normal=upper.cross(lower)
  if normal.length<1e-6:raise ValueError('Undefined knee hinge')
  desired[side+'.thigh']=Matrix.LocRotScale(h,hinge(upper,normal),V((1,1,1)));desired[side+'.shin']=Matrix.LocRotScale(k,hinge(lower,normal),V((1,1,1)));desired[side+'.foot']=foot
  shoulder=BM[side+'.upperarm'].translation;arm=torso@Matrix.Translation(shoulder)@Matrix.Rotation(math.radians(18)*math.cos(2*math.pi*phase),4,'X')@Matrix.Translation(-shoulder)
  for b in ['upperarm','forearm','hand']:desired[side+'.'+b]=arm@BM[side+'.'+b]
  metadata[side]={'phase':phase,'stance':phase<.6,'lift_m':lift,'world_root_y':-.32*u,'stance_segment':math.floor(u+offset),'knee':list(k),'ankle':list(a)}
 return desired,metadata
for i in range(65):
 u=i/64;desired,meta=pose(u)
 for name,mat in desired.items():
  b=rig.data.bones[name];pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';kwargs={'parent_matrix':desired[parents[name]],'parent_matrix_local':b.parent.matrix_local} if parents[name] else {};pb.matrix_basis=b.convert_local_to_pose(mat,b.matrix_local,invert=True,**kwargs)
 for pb in rig.pose.bones:
  for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=1+i)
for f in rig.animation_data.action.fcurves:
 for k in f.keyframe_points:k.interpolation='LINEAR'
sc.render.fps=80;sc.frame_start=1;sc.frame_end=65;sc.frame_set(1);rig.animation_data.action.name='original.walk.v53';out=P/'source/walk.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));records=[];groups={};lowest=1e9;highest_stance=0;length_error=0;loop_error=0;first=None
for i in range(257):
 u=i/256;sc.frame_set(1+int(u*64),subframe=(u*64)%1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();world={b.name:rig.matrix_world@b.head for b in rig.pose.bones};_,meta=pose(u);measured={}
 for side in ['left','right']:
  obj=bpy.data.objects[side+'.sole'].evaluated_get(deps);mesh=obj.to_mesh()
  try:vertices=[obj.matrix_world@v.co for v in mesh.vertices]
  finally:obj.to_mesh_clear()
  low=min(v.z for v in vertices);lowest=min(lowest,low);support=meta[side]['stance'];pt=vertices[0]+V((0,-.32*u,0));measured[side]={'minimum_sole_z':low,'stance':support,'fixed_sole_vertex_world':list(pt)}
  if support:
   highest_stance=max(highest_stance,abs(low));groups.setdefault((side,meta[side]['stance_segment']),[]).append(pt)
  for a,b in [('thigh','shin'),('shin','foot')]:length_error=max(length_error,abs((world[side+'.'+b]-world[side+'.'+a]).length-(BM[side+'.'+b].translation-BM[side+'.'+a].translation).length))
 if first is None:first=world
 if i==256:loop_error=max((world[n]-first[n]).length for n in world)
 records.append({'index':i,'phase':u,'source_bones':{n:list(p) for n,p in world.items()},'sole':measured})
drift=max(max((v-points[0]).length for v in points) for points in groups.values());checks={'saved_257_samples':len(records)==257,'stance_world_surface_drift_under_0_0002m':drift<.0002,'stance_surface_height_under_0_0002m':highest_stance<.0002,'no_floor_penetration_over_0_0002m':lowest>-.0002,'limb_length_error_under_0_0002m':length_error<.0002,'loop_bone_error_under_0_00001m':loop_error<.00001}
(P/'source/walk-source-review.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent_blend_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'checks':checks,'bounded_source_pass':all(checks.values()),'measurements':{'max_stance_world_sole_vertex_drift_m':drift,'max_stance_floor_error_m':highest_stance,'min_sole_height_m':lowest,'max_leg_length_error_m':length_error,'loop_max_bone_error_m':loop_error},'design':{'duration_ms':800,'stride_m':.32,'stance_fraction':.6,'swing_lift_m':.06,'root_speed_m_s':.4,'arm_swing_degrees':18},'records':records,'scope':'Original saved rig source/contact guide only. Actual source surface and limb checks do not certify any painted frame, hidden anatomy, costume or exported game behavior.'},indent=2)+'\n');print('WALK_SOURCE',json.dumps({'checks':checks,'drift':drift,'floor':highest_stance,'length_error':length_error}),flush=True)
assert all(checks.values())
