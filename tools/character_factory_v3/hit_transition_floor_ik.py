"""Bounded 3D two-bone ankle lift for a Hit-to-Idle floor-contact study.

Only negative selected skin heights during explicit transition frames are
adjusted. This is a candidate correction, not proof of correct contact.
"""
import math

def apply(rig, rec):
 import bpy
 from mathutils import Matrix,Vector
 from audit_swordsman_hit_frozen_feet import indices_by_weight
 if rec.get('transition_weight') is None:return {'applied':False,'reason':'not transition'}
 if rec['transition_weight']>=1.:return {'applied':False,'reason':'preserve exact target idle pose'}
 mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig)
 def point(name):return rig.matrix_world@rig.pose.bones[name].head
 def lowest(side):
  ids=indices_by_weight(mesh,side);obj=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());m=obj.to_mesh()
  try:
   if len(m.vertices)!=len(mesh.data.vertices):raise ValueError('evaluated topology changed')
   return min((obj.matrix_world@m.vertices[i].co).z for i in ids)
  finally:obj.to_mesh_clear()
 def aim(name,target):
  bone=rig.pose.bones[name];matrix=rig.matrix_world@bone.matrix;current=rig.matrix_world@bone.tail-matrix.translation;desired=target-matrix.translation
  if min(current.length,desired.length)<1e-7:raise ValueError('degenerate leg segment')
  rotation=current.normalized().rotation_difference(desired.normalized())@matrix.to_quaternion()
  bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(matrix.translation,rotation,matrix.to_scale());bpy.context.view_layer.update()
 result={}
 for side in ('l','r'):
  initial=lowest(side);lift=max(0.,-initial)
  if lift>.04:raise ValueError('foot correction exceeds 40 mm bound')
  if lift<1e-6:result[side]={'before_z_m':initial,'after_z_m':initial,'lift_m':0.,'reach_clamp_m':0.};continue
  thigh='thigh_'+side;calf='calf_'+side;foot='foot_'+side
  hip=point(thigh);knee=point(calf);ankle=point(foot);target=ankle+Vector((0,0,lift))
  foot_world=(rig.matrix_world@rig.pose.bones[foot].matrix).copy()
  upper=(knee-hip).length;lower=(ankle-knee).length;axis=target-hip;requested=axis.length
  if min(upper,lower,requested)<1e-7:raise ValueError('degenerate foot target')
  axis.normalize();distance=max(abs(upper-lower)+1e-6,min(upper+lower-1e-6,requested));goal=hip+axis*distance
  along=(upper*upper-lower*lower+distance*distance)/(2*distance);pole=knee-hip;pole-=axis*pole.dot(axis)
  if pole.length<1e-6:raise ValueError('ambiguous knee bend')
  pole.normalize();new_knee=hip+axis*along+pole*math.sqrt(max(0.,upper*upper-along*along))
  aim(thigh,new_knee);aim(calf,goal)
  foot_world.translation=point(foot);rig.pose.bones[foot].matrix=rig.matrix_world.inverted()@foot_world;bpy.context.view_layer.update()
  result[side]={'before_z_m':initial,'after_z_m':lowest(side),'lift_m':lift,'reach_clamp_m':abs(requested-distance),'ankle_error_m':(point(foot)-target).length}
 return {'applied':True,'feet':result}
