"""Isolated target-facing cast gaze, enabling a demonstrable head pose family.

This is authored motion adaptation, not unchanged mocap or accepted sprite art.
Only the head orientation changes; its position and every other body joint stay
protected. Source actions, camera, hand grip and character fit remain fixed.
"""
import math

RECORDS=[]

def apply_target_gaze(rig,job):
    import bpy
    from mathutils import Matrix,Quaternion
    profile=job['target_gaze_study']
    values=profile['reference_head_world_quaternion']
    if len(values)!=4 or not all(math.isfinite(v)for v in values):
        raise ValueError('Finite explicit world-space gaze quaternion required')
    target=Quaternion(values)
    if abs(target.magnitude-1)>1e-4:
        raise ValueError('Unit reference gaze quaternion required')
    target.normalize()
    limit=float(profile['maximum_correction_degrees'])
    if not 0<limit<=50:
        raise ValueError('Study correction must remain within 50 degrees')
    protected=[b.name for b in rig.pose.bones if b.name not in ['head','head_leaf']]
    before={n:(rig.matrix_world@rig.pose.bones[n].matrix).copy()for n in protected}
    head=rig.pose.bones['head']
    old=rig.matrix_world@head.matrix
    location,rotation,scale=old.decompose()
    correction=math.degrees(rotation.rotation_difference(target).angle)
    if correction>180:correction=360-correction
    if correction>limit:
        raise ValueError(f'Head correction {correction:.5f} exceeds reviewed neck range')
    head.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(location,target,scale)
    bpy.context.view_layer.update()
    actual=rig.matrix_world@head.matrix
    error=(actual.translation-location).length
    errors={n:max(abs((rig.matrix_world@rig.pose.bones[n].matrix)[r][c]-before[n][r][c])for r in range(4)for c in range(4))for n in protected}
    q=actual.to_quaternion().normalized()
    component_error=min(sum((q[i]-target[i])**2 for i in range(4))**.5,sum((q[i]+target[i])**2 for i in range(4))**.5)
    if error>2e-6 or max(errors.values())>2e-6 or component_error>3e-6:
        raise ValueError('Gaze study changed protected anatomy or missed the target rotation')
    RECORDS.append({'correction_degrees':correction,'head_position_error_m':error,'head_world_rotation_component_error':component_error,'maximum_protected_body_matrix_error':max(errors.values()),'protected_bone_count':len(protected),'head_scale':list(scale),'head_world_quaternion':list(q)})
