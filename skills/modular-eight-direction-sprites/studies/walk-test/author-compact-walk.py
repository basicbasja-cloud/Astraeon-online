"""Author a compact original gait on the existing original mesh/rig.

Lower-body endpoints are authored, not extracted from RO. Upper-body local
rotations reuse a damped CC0-derived original template. No source file is edited.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent/'source-motion'))
from retarget_math import two_segment
sys.path.insert(0,str(Path(__file__).parent))
from compact_gait_math import foot_path,roll
def main():
 p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 if a.output.exists():raise ValueError('Fresh source output required')
 bpy.ops.wm.open_mainfile(filepath=str(a.blend));scene=bpy.context.scene;rig=bpy.data.objects['original.walk.rig'];pivot=bpy.data.objects['facing.pivot'];pivot.rotation_euler.z=0;bpy.context.view_layer.update()
 original=json.loads((a.blend.parent/'motion.json').read_text());names=[b.name for b in rig.data.bones];rest={n:rig.data.bones[n].matrix_local.copy() for n in names};parents={n:rig.data.bones[n].parent.name if rig.data.bones[n].parent else None for n in names}
 times=[i/128 for i in range(129)];sampled=[]
 for u in times:
  f=u*original['duration_seconds']*1000;scene.frame_set(math.floor(f),subframe=f%1);bpy.context.view_layer.update();world={n:rig.pose.bones[n].matrix.copy() for n in names};sampled.append({n:(world[parents[n]].inverted()@world[n] if parents[n] else world[n]) for n in names})
 sole_data={}
 for side,suffix in [('left','l'),('right','r')]:
  sole_data[side]=[]
  for part,bone in [('heel','foot_'+suffix),('toe','ball_'+suffix)]:
   o=bpy.data.objects[f'sole.{side}.{part}'];groups={g.name for g in o.vertex_groups}
   if groups!={bone}:raise ValueError('This source sole needs an explicit one-bone adapter')
   sole_data[side].append((bone,[o.matrix_world@v.co for v in o.data.vertices]))
 rig.animation_data_clear();duration=.8;frames=[];max_length=0;minimum=1;flat={s:[] for s in sole_data}
 for i,u in enumerate(times):
  desired={}
  for n in names:
   local=sampled[i][n];q=sampled[0][n].to_quaternion().slerp(local.to_quaternion(),.55 if n.startswith(('upperarm','lowerarm','hand','clavicle')) else .25)
   m=q.to_matrix().to_4x4();m.translation=local.translation
   if n.startswith(('spine_','neck_','Head','thigh_')):
    # Neutral authored anatomy, not the template's forward-leaning spine.
    m=rest[parents[n]].inverted()@rest[n]
   desired[n]=desired[parents[n]]@m if parents[n] else m
   if n=='root':desired[n]=Matrix.Identity(4)
   if n=='pelvis':
    desired[n]=Matrix.Rotation(math.radians(1.2)*math.sin(2*math.pi*u),4,'Z')@rest[n];desired[n].translation=Vector((.004*math.sin(2*math.pi*u),.030,.570-.004*math.cos(4*math.pi*u)))
  targets={};support={}
  for side,suffix,offset in [('left','l',0),('right','r',.5)]:
   phase=(u+offset)%1;y,height=foot_path(phase);ft='foot_'+suffix;hip='thigh_'+suffix;kn='calf_'+suffix
   qroll=Matrix.Rotation(roll(phase),4,'X');foot=qroll@rest[ft];foot.translation=Vector((rest[ft].translation.x,y,rest[ft].translation.z));delta=foot@rest[ft].inverted()
   cluster=[n for n in names if n==ft or ft in [b.name for b in rig.data.bones[n].parent_recursive]]
   for n in cluster:desired[n]=delta@rest[n]
   low=min((desired[bone]@rest[bone].inverted()@v).z for bone,vertices in sole_data[side] for v in vertices);dz=height+.001-low
   for n in cluster:desired[n].translation.z+=dz
   h=desired[hip].translation.copy();goal=desired[ft].translation.copy();l1=(rest[kn].translation-rest[hip].translation).length;l2=(rest[ft].translation-rest[kn].translation).length
   answer=two_segment(h,h+Vector((0,-.24,-.20)),goal,l1,l2)
   if not answer['reachable']:raise ValueError(f'Unreachable compact gait endpoint: phase{phase} {side}, distance{answer["reach_distance"]}, length{l1+l2}; re-author, never stretch')
   k=Vector(answer['middle'].tolist())
   for bone,child,base,end in [(hip,kn,h,k),(kn,ft,k,goal)]:
    before=rest[child].translation-rest[bone].translation;after=end-base;mat=before.rotation_difference(after).to_matrix()@rest[bone].to_3x3();desired[bone]=mat.to_4x4();desired[bone].translation=base
   max_length=max(max_length,abs((k-h).length-l1),abs((goal-k).length-l2));targets[side]={'phase':phase,'ankle':list(goal),'planned_swing_height':height,'flat_support':.07<=phase<=.50};support[side]=phase<.60
  for n in names:
   bone=rig.data.bones[n];kwargs={'parent_matrix':desired[parents[n]],'parent_matrix_local':bone.parent.matrix_local} if parents[n] else {};pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix_basis=bone.convert_local_to_pose(desired[n],bone.matrix_local,invert=True,**kwargs)
  bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();soles={}
  for side,suffix in [('left','l'),('right','r')]:
   soles[side]={}
   for part in ['heel','toe']:
    o=bpy.data.objects[f'sole.{side}.{part}'].evaluated_get(deps);mesh=o.to_mesh()
    try:
     verts=[o.matrix_world@v.co for v in mesh.vertices];low=min(v.z for v in verts);minimum=min(minimum,low);soles[side][part]={'minimum_mesh_z':low,'fixed_vertex_world_traveled':list(verts[0]+Vector((0,-.42*u,0)))}
    finally:o.to_mesh_clear()
   if targets[side]['flat_support']:flat[side].append(soles[side]['heel']['fixed_vertex_world_traveled'])
  for n in names:
   for prop in ['location','rotation_quaternion','scale']:rig.pose.bones[n].keyframe_insert(prop,frame=u*duration*1000)
  frames.append({'source_index':i,'time_seconds':u*duration,'root_world':[0,-.42*u,0],'in_place_joints':{n:list(rig.pose.bones[n].head) for n in names},'authored_foot_targets':targets,'authored_stance':support,'actual_sole_samples':soles})
 action=rig.animation_data.action;action.name='original.compact.contact-walk';action.use_fake_user=True
 for curve in action.fcurves:
  for k in curve.keyframe_points:k.interpolation='LINEAR'
 if minimum<-.002 or max_length>2e-5:raise ValueError('Compact gait failed actual mesh/length checks')
 # Flat support is checked per contiguous interval, never across separate steps.
 lock=[]
 for side in ['left','right']:
  groups=[];active=[]
  for f in frames:
   if f['authored_foot_targets'][side]['flat_support']:active.append(f['actual_sole_samples'][side]['heel']['fixed_vertex_world_traveled'])
   elif active:groups.append(active);active=[]
  if active:groups.append(active)
  for g in groups:
   anchor=Vector(g[0]);lock.append(max((Vector(v)-anchor).length for v in g))
 if max(lock)>1e-4:raise ValueError('Authored flat-support world vertex drift exceeds tolerance')
 report={**original,'schema':'original-compact-gait-v1','duration_seconds':duration,'source_samples':len(frames),'frames':frames,'selected_source_indices':list(range(0,128,16)),'pose_authoring':'New compact original lower-body trajectories/heel-toe roll and fixed-length IK; neutral-rest upright spine/head, small authored pelvis yaw, damped CC0-derived original arms','source_parent_blend_sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest(),'source_pose_edited':True,'stride_world':.42,'stance_fraction':.60,'swing_height_world':.040,'pelvis_bob_amplitude_world':.004,'pelvis_base_height_world':.570,'upright_spine_from_rest':True,'max_anatomical_leg_length_error':max_length,'minimum_actual_sole_z_at_bake_samples':minimum,'max_fixed_heel_vertex_drift_during_flat_support_world':max(lock),'world_lock_scope':'Actual fixed heel vertex at129 bake keys within authored flat-support intervals only. Rolling heel/toe contacts and interpolated half-keys are not certified. Not support-force/balance or painted-image proof.','release_ready':False}
 a.output.mkdir(parents=True);(a.output/'motion.json').write_text(json.dumps(report,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(a.output/'original-modular-walk.blend'),compress=True);print('COMPACT_GAIT',minimum,max_length,max(lock))
if __name__=='__main__':main()
