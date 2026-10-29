"""Bounded 3D left-arm reach for an isolated Swordsman pickup study.

This is not a full-body contact solver or a production motion. It preserves the
source elbow bend side and wrist world orientation while shifting its target.
"""
import math

def reach_weight(source_frame):
 if not math.isfinite(source_frame):raise ValueError('Invalid source frame')
 return max(0.,min(1.,(source_frame-10.)/15.,(150.-source_frame)/15.))

def apply(rig,source_frame,depth,inward=0.):
 import bpy
 from mathutils import Matrix,Vector
 if not math.isfinite(depth) or not 0<=depth<=.30 or not math.isfinite(inward) or not 0<=inward<=.25:raise ValueError('Invalid bounded reach target')
 w=reach_weight(source_frame)
 if w==0 or depth==0:return {'weight':w,'reach_clamp_m':0.}
 def point(name):return rig.matrix_world@rig.pose.bones[name].head
 shoulder=point('upperarm_l');elbow=point('lowerarm_l');wrist=point('hand_l')
 hand_world=(rig.matrix_world@rig.pose.bones['hand_l'].matrix).copy();target=wrist+Vector((0,0,-depth*w))
 horizontal=shoulder-wrist;horizontal.z=0
 if horizontal.length>1e-6:target+=horizontal.normalized()*(inward*w)
 upper=(elbow-shoulder).length;lower=(wrist-elbow).length;axis=target-shoulder;requested=axis.length
 if requested<1e-6 or min(upper,lower)<1e-6:raise ValueError('Degenerate left arm geometry')
 axis.normalize();distance=max(abs(upper-lower)+1e-5,min(upper+lower-1e-5,requested));goal=shoulder+axis*distance
 along=(upper*upper-lower*lower+distance*distance)/(2*distance);pole=elbow-shoulder;pole-=axis*pole.dot(axis)
 if pole.length<1e-5:raise ValueError('Degenerate elbow bend direction')
 pole.normalize();new_elbow=shoulder+axis*along+pole*math.sqrt(max(0,upper*upper-along*along))
 for name,end in [('upperarm_l',new_elbow),('lowerarm_l',goal)]:
  bone=rig.pose.bones[name];matrix=rig.matrix_world@bone.matrix;current=rig.matrix_world@bone.tail-matrix.translation;desired=end-matrix.translation
  if min(current.length,desired.length)<1e-6:raise ValueError('Degenerate arm bone direction')
  rotation=current.normalized().rotation_difference(desired.normalized())@matrix.to_quaternion()
  bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(matrix.translation,rotation,matrix.to_scale());bpy.context.view_layer.update()
 hand_world.translation=point('hand_l');rig.pose.bones['hand_l'].matrix=rig.matrix_world.inverted()@hand_world;bpy.context.view_layer.update()
 return {'weight':w,'requested_wrist':list(target),'actual_wrist':list(point('hand_l')),'reach_clamp_m':max(0.,requested-distance)}
