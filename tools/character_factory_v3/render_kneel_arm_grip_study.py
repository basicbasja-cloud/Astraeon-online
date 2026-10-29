"""Isolated native-rig study: resample kneel and rotate only sword upper arm.

The source action, production renderer and bindings are never modified. This is
not a motion, grip, contact, art, or runtime approval.
"""
import hashlib,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from render_kneel_pickup_sampling_study import validate_samples
CANONICAL=HERE/'render_patch001_guides.py'
SAMPLE='f=start+(end-start)*local'
POSE="        for name,matrix in staff_pose.items():rig.pose.bones[name].matrix_basis=matrix\n"
INTERVALS="    intervals=job.get('source_ranges',{})\n"

def validate(job):
 validate_samples(job)
 axis=job.get('study_arm_axis');angle=job.get('study_arm_degrees')
 if axis not in ('X','Y','Z') or type(angle) not in (int,float) or not math.isfinite(angle) or abs(angle)>50:raise ValueError('Expected a finite bounded single-axis arm adjustment')
 if type(job.get('study_closed_fingers',False)) is not bool:raise ValueError('Expected an explicit boolean for the grip study')
 if type(job.get('study_blade_clearance',False)) is not bool:raise ValueError('Expected an explicit boolean for blade clearance diagnostics')
 depth=job.get('study_left_reach_m',0.)
 if type(depth) not in (int,float) or not math.isfinite(depth) or not 0<=depth<=.30:raise ValueError('Expected a bounded left-arm reach')
 inward=job.get('study_left_inward_m',0.)
 if type(inward) not in (int,float) or not math.isfinite(inward) or not 0<=inward<=.25:raise ValueError('Expected a bounded inward reach')
 wrist=job.get('study_left_wrist_degrees',0.)
 if type(wrist) not in (int,float) or not math.isfinite(wrist) or abs(wrist)>45:raise ValueError('Expected a bounded left wrist angle')
 spine=job.get('study_spine_x_degrees',0.)
 if type(spine) not in (int,float) or not math.isfinite(spine) or abs(spine)>20:raise ValueError('Expected a bounded spine angle')
 samples=job['study_source_frames']
 if samples[0]!=0 or samples[-1]!=156:raise ValueError('Study envelope assumes the preserved original endpoints')

def main():
 import bpy
 from bpy.app.handlers import persistent
 args=sys.argv[sys.argv.index('--')+1:];job=json.loads(Path(args[args.index('--job')+1]).read_text());validate(job)
 source=CANONICAL.read_text()
 if hashlib.sha256(CANONICAL.read_bytes()).hexdigest()!=job['renderer_sha256'] or source.count(SAMPLE)!=1 or source.count(POSE)!=1 or source.count(INTERVALS)!=1:raise ValueError('Pinned canonical renderer changed')
 source=source.replace(SAMPLE,"f=job['study_source_frames'][i]\n        if not start<=f<=end:raise ValueError('Study frame outside action range')")
 grip_reference="""    finger_reference={}
    study_reach_info={}
    if job.get('study_closed_fingers',False):
        action('Idle_Sword');sc.frame_set(0);bpy.context.view_layer.update()
        prefixes=('index_','middle_','ring_','pinky_','thumb_')
        finger_reference={b.name:b.matrix_basis.copy() for b in rig.pose.bones if b.name.endswith('_r') and b.name.startswith(prefixes) and 'leaf' not in b.name}
        if len(finger_reference)!=15:raise ValueError('Unexpected native sword hand')
"""
 source=source.replace(INTERVALS,grip_reference+INTERVALS)
 addition="""        t=sc.frame_current_final
        weight=max(0.,min(1.,t/30.,(156.-t)/26.))
        if job.get('study_spine_x_degrees',0.):
            from kneel_pickup_reach_study import reach_weight
            spine=rig.pose.bones['spine_01']
            spine.matrix_basis=spine.matrix_basis @ Matrix.Rotation(math.radians(job['study_spine_x_degrees'])*reach_weight(t),4,'X')
            bpy.context.view_layer.update()
        arm=rig.pose.bones['upperarm_r']
        arm.matrix_basis=arm.matrix_basis @ Matrix.Rotation(math.radians(job['study_arm_degrees'])*weight,4,job['study_arm_axis'])
        for name,matrix in finger_reference.items():rig.pose.bones[name].matrix_basis=matrix.copy()
        bpy.context.view_layer.update()
        study_reach_info.clear()
        if job.get('study_left_reach_m',0.):
            from kneel_pickup_reach_study import apply,reach_weight
            study_reach_info.update(apply(rig,t,job['study_left_reach_m'],job.get('study_left_inward_m',0.)))
            wrist=rig.pose.bones['hand_l']
            wrist.matrix_basis=wrist.matrix_basis @ Matrix.Rotation(math.radians(job.get('study_left_wrist_degrees',0.))*reach_weight(t),4,'X')
            bpy.context.view_layer.update()
"""
 source=source.replace(POSE,POSE+addition)
 clearance_records=[]
 if job.get('study_blade_clearance',False):
  if job.get('weapon')!='sword':raise ValueError('Blade diagnostics require a sword')
  from mathutils.bvhtree import BVHTree
  def sample_clearance(direction,frame,grip,axis,bones,rig,reach_info):
   depsgraph=bpy.context.evaluated_depsgraph_get();objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render]
   if len(objects)!=1 or objects[0].name!='Mannequin':raise ValueError('Unexpected visible study geometry')
   obj=objects[0];tree=BVHTree.FromObject(obj,depsgraph);inverse=obj.matrix_world.inverted()
   # Start beyond the grip and guard: this is a thin proxy centerline, not a blade mesh.
   a=grip+axis*.12;b=grip+axis*.8;local_a=inverse@a;local_b=inverse@b;delta=local_b-local_a;length=delta.length
   hit,normal,index,distance=tree.ray_cast(local_a,delta.normalized(),length)
   # Positive control: a line through the torso should intersect the evaluated mesh.
   control_a=bones['head']+type(axis)((0,0,.3));control_b=bones['pelvis']-type(axis)((0,0,.3))
   control_start=inverse@control_a;control_delta=(inverse@control_b)-control_start
   control_hit,_,_,_=tree.ray_cast(control_start,control_delta.normalized(),control_delta.length)
   evaluated=obj.evaluated_get(depsgraph);mesh=evaluated.to_mesh()
   try:
    lowest_vertex=min(mesh.vertices,key=lambda vertex:(evaluated.matrix_world@vertex.co).z)
    lowest_index=lowest_vertex.index;lowest_world=list(evaluated.matrix_world@lowest_vertex.co);lowest_mesh_z=lowest_world[2]
    weights=sorted(({'bone':obj.vertex_groups[g.group].name,'weight':g.weight} for g in obj.data.vertices[lowest_index].groups),key=lambda x:-x['weight'])[:4]
   finally:evaluated.to_mesh_clear()
   nearest=[]
   for i in range(18):
    point=a.lerp(b,i/17);result=tree.find_nearest(inverse@point)
    if result[0] is None:raise ValueError('Empty mannequin BVH')
    nearest.append((point-(obj.matrix_world@result[0])).length)
   tips={name:list(rig.matrix_world@rig.pose.bones[name].tail) for name in ('index_03_l','middle_03_l','ring_03_l','pinky_03_l','thumb_03_l')}
   clearance_records.append({'direction':direction,'frame':frame,'blade_centerline_start_offset_m':.12,'blade_centerline_end_offset_m':.8,'blade_start_world_m':list(a),'blade_end_world_m':list(b),'proxy_radius_m':.022,'lowest_proxy_height_over_z0_m':min(a.z,b.z)-.022,'lowest_evaluated_mesh_vertex_z_m':lowest_mesh_z,'lowest_vertex_index':lowest_index,'lowest_vertex_world_m':lowest_world,'lowest_vertex_skin_weights':weights,'left_distal_bone_tails_world_m':tips,'left_reach':reach_info,'centerline_surface_hit':hit is not None,'first_hit_world':list(obj.matrix_world@hit) if hit is not None else None,'minimum_sampled_surface_distance_m':min(nearest),'torso_positive_control_hit':control_hit is not None})
  marker="            path=folder/f'{i:03d}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)"
  if source.count(marker)!=1:raise ValueError('Canonical output point changed')
  source=source.replace(marker,"            sample_clearance(direction,i,grip,axis,bones,rig,dict(study_reach_info))\n"+marker)
 @persistent
 def freeze(scene):
  for actor in [o for o in bpy.data.objects if o.type=='ARMATURE' and o.animation_data and o.animation_data.action]:
   basis={b.name:b.matrix_basis.copy() for b in actor.pose.bones}
   world={b.name:(actor.matrix_world@b.matrix).copy() for b in actor.pose.bones}
   actor.animation_data.action=None
   for bone in actor.pose.bones:bone.matrix_basis=basis[bone.name]
   bpy.context.view_layer.update()
   error=max((max(abs((actor.matrix_world@b.matrix)[r][c]-world[b.name][r][c]) for r in range(4) for c in range(4)) for b in actor.pose.bones),default=0.)
   if error>1e-5:raise ValueError('Frozen study pose changed')
 bpy.app.handlers.render_pre.append(freeze)
 try:
  scope={'__name__':'__main__','__file__':str(CANONICAL)}
  if job.get('study_blade_clearance',False):scope['sample_clearance']=sample_clearance
  exec(compile(source,str(CANONICAL),'exec'),scope)
  if job.get('study_blade_clearance',False):
   output=Path(args[args.index('--output')+1]);(output/'blade-clearance-diagnostic.json').write_text(json.dumps({'status':'THIN_CENTERLINE_VS_EVALUATED_MANNEQUIN_NOT_FULL_COLLISION_APPROVAL','records':clearance_records},indent=2)+'\n')
 finally:
  if freeze in bpy.app.handlers.render_pre:bpy.app.handlers.render_pre.remove(freeze)
if __name__=='__main__':main()
