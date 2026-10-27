"""Compute a staff-specific reference grip; body motion remains source-authored."""
import math
import numpy as np


def alignment_angles(forearm_axis,knuckle_axis,up=(0,0,1)):
    def unit(v):
        v=np.asarray(v,dtype=float);length=np.linalg.norm(v)
        if not np.isfinite(v).all() or length<1e-9:raise ValueError('Nonzero finite grip axes required')
        return v/length
    d,v,z=map(unit,[forearm_axis,knuckle_axis,up]);a=v-d*np.dot(d,v);b=z-d*np.dot(d,z)
    if min(np.linalg.norm(a),np.linalg.norm(b))<1e-8:raise ValueError('Degenerate forearm/grip alignment')
    a=unit(a);b=unit(b);roll=math.atan2(np.dot(d,np.cross(a,b)),np.dot(a,b))
    rotated=v*math.cos(roll)+np.cross(d,v)*math.sin(roll)+d*np.dot(d,v)*(1-math.cos(roll))
    flex=math.acos(float(np.clip(np.dot(rotated,z),-1,1)))
    return {'forearm_roll_radians':roll,'wrist_flex_radians':flex,'rolled_knuckle_axis':rotated.tolist(),'target_axis':z.tolist()}


def apply_reference_staff_grip(rig,job):
    import bpy
    from mathutils import Matrix,Vector,Quaternion
    if job.get('held_staff_hand')!='r' or job.get('weapon')!='staff':raise ValueError('Only original human right-staff study supported')
    bones=rig.pose.bones;world=lambda n:rig.matrix_world@bones[n].head
    before={n:world(n).copy() for n in ['head','pelvis','foot_r','foot_l','hand_r','hand_l','lowerarm_r']}
    axis=(world('hand_r')-world('lowerarm_r')).normalized();knuckles=world('index_01_r')-world('pinky_01_r');angles=alignment_angles(axis,knuckles)
    if abs(math.degrees(angles['forearm_roll_radians']))>100 or math.degrees(angles['wrist_flex_radians'])>35:raise ValueError('Reference grip exceeds study articulation bounds')
    roll=Quaternion(axis,angles['forearm_roll_radians']);bone=bones['lowerarm_r'];w=rig.matrix_world@bone.matrix;loc,rot,scale=w.decompose();bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(loc,roll@rot,scale);bpy.context.view_layer.update()
    current=(world('index_01_r')-world('pinky_01_r')).normalized();flex=current.rotation_difference(Vector((0,0,1)));hand=bones['hand_r'];loc,rot,scale=(rig.matrix_world@hand.matrix).decompose();hand.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(loc,flex@rot,scale);bpy.context.view_layer.update()
    residual=math.degrees((world('index_01_r')-world('pinky_01_r')).normalized().angle(Vector((0,0,1))));errors={n:(world(n)-p).length for n,p in before.items()}
    if max(errors.values())>1e-5 or residual>1e-3:raise ValueError('Grip alignment moved body anchors or failed axis constraint')
    return {'reference_action':job['staff_arm_reference'],'forearm_roll_degrees':math.degrees(angles['forearm_roll_radians']),'wrist_flex_degrees':math.degrees(angles['wrist_flex_radians']),'aligned_reference_axis_error_degrees':residual,'reference_anchor_errors_m':errors}
