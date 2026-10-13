"""v26 independent saved-source checks: fixed modeled soles and hidden right-hand trajectory only."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

p=argparse.ArgumentParser();p.add_argument('--index',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=json.loads(a.index.read_text());blend=Path(source['blend']);assert hashlib.sha256(blend.read_bytes()).hexdigest()==source['blend_sha256'];assert hashlib.sha256(Path(source['parent_walk_blend']).read_bytes()).hexdigest()==source['parent_walk_sha256']
bpy.ops.wm.open_mainfile(filepath=str(blend),use_scripts=False);s=bpy.context.scene;r=bpy.data.objects['original.walk.rig'];pivot=bpy.data.objects['facing.pivot'];palm=bpy.data.objects[source.get('palm_geometry_object','glove.right.palm')];handle=bpy.data.objects['v26.sword.handle'];blade=bpy.data.objects['v26.sword.blade'];action=r.animation_data.action;assert s.frame_end==source['duration_ms'],'Source clock disagrees with saved scene';assert action.name=='original.diagonal.blade.slash.v26';assert handle['anatomical_owner']=='right';assert {g.name for g in handle.vertex_groups}=={'hand_r'}
def verts(obj):
 e=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=e.to_mesh()
 try:return [e.matrix_world@v.co for v in mesh.vertices]
 finally:e.to_mesh_clear()
def center(obj):v=verts(obj);return sum(v,Vector())/len(v)
maximum_pose_error=0;maximum_palm_hilt_error=0;minimum_sole=1;maximum_plant_drift=0;maximum_length_error=0;maximum_camera_error=0;checks=0;head_xy=[];minimum_wrist_to_palm=1
rest=r.data.bones
for view,number in [('SE',1)]:
 pivot.rotation_euler.z=number*math.pi/4;anchors={}
 for t in range(0,source['duration_ms']+1,5):
  s.frame_set(t);bpy.context.view_layer.update();checks+=1;pc=center(palm);hc=center(handle);maximum_palm_hilt_error=max(maximum_palm_hilt_error,(pc-hc).length);minimum_wrist_to_palm=min(minimum_wrist_to_palm,(pc-r.matrix_world@r.pose.bones['hand_r'].head).length)
  for side in ['right','left']:
   for part in ['heel','toe']:
    name='sole.'+side+'.'+part;vs=verts(bpy.data.objects[name]);minimum_sole=min(minimum_sole,min(v.z for v in vs));anchors.setdefault(name,vs[0]);maximum_plant_drift=max(maximum_plant_drift,(vs[0]-anchors[name]).length)
  for suf in ['r','l']:
   for chain in [('thigh','calf','foot'),('upperarm','lowerarm','hand')]:
    for b,c in zip(chain,chain[1:]):
     name=b+'_'+suf;child=c+'_'+suf;maximum_length_error=max(maximum_length_error,abs((r.pose.bones[name].head-r.pose.bones[child].head).length-(rest[name].head_local-rest[child].head_local).length))
  for rec in source['records']:
   if rec['view']==view and rec['time_ms']==t:
    for n,value in rec['bones'].items():maximum_pose_error=max(maximum_pose_error,(r.matrix_world@r.pose.bones[n].head-Vector(value['world'])).length)
    q=world_to_camera_view(s,s.camera,pc);actual=Vector((q.x*512,(1-q.y)*512));maximum_camera_error=max(maximum_camera_error,(actual-Vector(rec['right_grip_xy'])).length)
    assert (r.matrix_world@r.pose.bones['root'].head).length<1e-6
    h=r.matrix_world@r.pose.bones['Head'].head;head_xy.append([view,t,list(h)])
assert handle.hide_render and blade.hide_render,'A rigid weapon must not be rendered in hand-tail mode'
assert maximum_palm_hilt_error<2e-6 and minimum_wrist_to_palm>.005,'Source socket is not actual palm'
assert minimum_sole>=-.002 and maximum_plant_drift<2e-6 and maximum_length_error<2e-6
assert maximum_pose_error<2e-6 and maximum_camera_error<.002
assert (Vector(source['dense_bake'][0]['hip'])-Vector(source['dense_bake'][-1]['hip'])).length<1e-8
# Independently re-evaluate the hidden blade basis, not just the hand joint.
normal=Vector(source['swing_plane_normal_facing_local']);axis_error=0;edge_error=0;angles=[]
u=Vector((-.5,0,.8660254)).normalized();v=Vector((0,-1,0))
for row in source['dense_bake']:
 t=row['time_ms'];s.frame_set(t);bpy.context.view_layer.update()
 actual=r.pose.bones['hand_r'].matrix.to_3x3().col[1].normalized()
 recorded=(Vector(row['blade_tip'])-Vector(row['right_grip'])).normalized()
 axis_error=max(axis_error,(actual-recorded).length)
 edge=r.pose.bones['hand_r'].matrix.to_3x3().col[2].normalized();edge_error=max(edge_error,(edge-normal).length)
 if 180<=t<=360:angles.append(math.degrees(math.atan2(actual.dot(v),actual.dot(u))))
assert axis_error<2e-6 and edge_error<2e-6
assert all(b>=a-1e-5 for a,b in zip(angles,angles[1:])), 'Cut rotates backwards inside its declared plane'
report={'schema':'reopened-diagonal-blade-slash-check-v26','source_index':str(a.index),'source_index_sha256':hashlib.sha256(a.index.read_bytes()).hexdigest(),'source_blend_sha256':source['blend_sha256'],'blender':bpy.app.version_string,'actual_evaluated_pose_count':checks,'physical_facings':1,'minimum_actual_sole_z':minimum_sole,'maximum_fixed_source_sole_vertex_drift_world':maximum_plant_drift,'maximum_actual_segment_length_error_world':maximum_length_error,'maximum_reopened_pose_error_world':maximum_pose_error,'maximum_actual_palm_mesh_to_hilt_mesh_center_error_world':maximum_palm_hilt_error,'minimum_wrist_joint_to_palm_geometry_center_distance_world':minimum_wrist_to_palm,'maximum_palm_capture_projection_error_px':maximum_camera_error,'maximum_actual_blade_axis_replay_error':axis_error,'maximum_actual_fixed_edge_normal_error':edge_error,'active_cut_angle_start_end_degrees':[angles[0],angles[-1]],'finger_wrapping_verified':False,'painted_hand_or_contact_pass':False,'source_acting_approval':False,'scope':'Independent saved-file actual mesh/bone/socket/camera checks at137times×1view. Palm center coincidence is not finger wrapping or artist acceptance.'};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n');print('REOPENED_SWORD_SOURCE_OK',checks,maximum_palm_hilt_error,minimum_sole,maximum_plant_drift)
