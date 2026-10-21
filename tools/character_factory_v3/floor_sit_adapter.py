"""Authored 3D floor-contact correction for the source chair-sitting clip.

Keep native upper-body motion; lower the pelvis and solve two-bone legs against
floor ankle targets. This is explicitly adapted source motion, never raw mocap.
"""
import math
import bpy
from mathutils import Vector,Matrix


def apply_floor_sit(rig,phase):
    weight=max(0.,min(1.,phase));weight=weight*weight*(3-2*weight)
    pelvis=rig.pose.bones['pelvis'];world=rig.matrix_world@pelvis.matrix
    floor=(rig.matrix_world@rig.pose.bones['root'].head).z
    root=rig.matrix_world@rig.pose.bones['root'].head
    feet={s:(rig.matrix_world@rig.pose.bones['foot_'+s].matrix).copy()for s in ['l','r']}
    world.translation.z+=(floor+.20-world.translation.z)*weight
    pelvis.matrix=rig.matrix_world.inverted()@world;bpy.context.view_layer.update()
    def point(name):return rig.matrix_world@rig.pose.bones[name].head
    def aim(name,target):
        bone=rig.pose.bones[name];matrix=rig.matrix_world@bone.matrix
        current=rig.matrix_world@bone.tail-matrix.translation;desired=target-matrix.translation
        if current.length<1e-6 or desired.length<1e-6:raise ValueError('Degenerate IK segment '+name)
        rotation=current.normalized().rotation_difference(desired.normalized())@matrix.to_quaternion()
        bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(matrix.translation,rotation,matrix.to_scale());bpy.context.view_layer.update()
    for side,sign in [('l',1),('r',-1)]:
        thigh='thigh_'+side;calf='calf_'+side;foot='foot_'+side
        ankle_start=feet[side].translation;ankle_end=Vector((root.x+sign*.20,root.y-.50,floor+.10));ankle=ankle_start.lerp(ankle_end,weight)
        hip=point(thigh);knee=point(calf);old_ankle=point(foot)
        upper=(knee-hip).length;lower=(old_ankle-knee).length;axis=ankle-hip;distance=axis.length
        if distance<1e-6:raise ValueError('Degenerate floor ankle target')
        axis.normalize();distance=max(abs(upper-lower)+1e-5,min(upper+lower-1e-5,distance))
        along=(upper*upper-lower*lower+distance*distance)/(2*distance)
        height=math.sqrt(max(0,upper*upper-along*along));pole=Vector((0,0,1));pole-=axis*pole.dot(axis)
        if pole.length<.05:pole=Vector((0,-1,0));pole-=axis*pole.dot(axis)
        pole.normalize();target_knee=hip+axis*along+pole*height
        aim(thigh,target_knee);aim(calf,ankle)
        matrix=feet[side].copy();matrix.translation=point(foot);rig.pose.bones[foot].matrix=rig.matrix_world.inverted()@matrix;bpy.context.view_layer.update()
