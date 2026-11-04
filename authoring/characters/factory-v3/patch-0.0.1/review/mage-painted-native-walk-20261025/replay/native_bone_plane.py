"""Project a canonical bone's 3D rotation onto a fixed sprite camera plane.

Used for feet whose projected ankle/toe segment can be almost zero length.
World transforms come from the frozen Blender retargeter, never image fitting.
"""
import numpy as np
from scipy.spatial.transform import Rotation


def proper_rotation(matrix):
    value=np.asarray(matrix,float)
    if value.shape!=(4,4)or not np.isfinite(value).all():raise ValueError('Finite canonical 4x4 matrix required')
    u,s,v=np.linalg.svd(value[:3,:3])
    if min(s)<1e-8:raise ValueError('Degenerate canonical bone scale')
    rotation=u@v
    if np.linalg.det(rotation)<0:raise ValueError('Reflected canonical bone transform')
    return rotation


def bone_plane_matrix(source_world,target_world,camera,source_anchor,target_anchor):
    camera_rotation=Rotation.from_euler('xyz',camera['rotation']).as_matrix()
    basis=np.column_stack([camera_rotation[:,0],-camera_rotation[:,1]])
    delta=proper_rotation(target_world)@proper_rotation(source_world).T
    linear=basis.T@delta@basis
    if np.linalg.det(linear)<.05:raise ValueError('Bone plane changes side or approaches edge-on')
    a=np.asarray(source_anchor,float);b=np.asarray(target_anchor,float)
    if a.shape!=(2,)or b.shape!=(2,)or not np.isfinite([a,b]).all():raise ValueError('Finite projected anchors required')
    return np.column_stack([linear,b-linear@a])
