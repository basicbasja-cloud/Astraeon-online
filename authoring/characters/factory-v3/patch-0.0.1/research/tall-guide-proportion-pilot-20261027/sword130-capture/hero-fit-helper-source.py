"""Bounded, isolated guide proportion study; never final painted character art."""
import math

RECORDS=[]


def apply_fit(rig,job):
    import bpy
    from mathutils import Vector
    profile=job['hero_fit_study']
    torso=float(profile['torso_length_scale']);head=float(profile['head_scale'])
    if not (.65<=torso<=1 and 1<=head<=1.8) or not all(math.isfinite(v)for v in [torso,head]):
        raise ValueError('Study profile outside bounded proportion range')
    if rig.type!='ARMATURE' or 'spine_03' not in rig.pose.bones:
        raise ValueError('Original Mesh2Motion human guide required')
    protected=['root','pelvis','thigh_r','calf_r','foot_r','thigh_l','calf_l','foot_l']
    before={n:(rig.matrix_world@rig.pose.bones[n].matrix).copy()for n in protected}
    for bone in rig.data.bones:bone.inherit_scale='NONE'
    for name in ['spine_01','spine_02','spine_03','neck_01']:
        rig.pose.bones[name].scale=Vector((1,torso,1))
    for name in ['head','head_leaf']:rig.pose.bones[name].scale=Vector((head,head,head))
    bpy.context.view_layer.update()
    errors={n:max(abs((rig.matrix_world@rig.pose.bones[n].matrix)[r][c]-before[n][r][c])for r in range(4)for c in range(4))for n in protected}
    if max(errors.values())>2e-6:raise ValueError('Study changed protected lower-body matrices')
    RECORDS.append({'protected_matrix_errors':errors,'torso_scale':torso,'head_scale':head})
