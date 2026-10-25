import sys
from pathlib import Path
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from native_bone_plane import bone_plane_matrix,proper_rotation


class BonePlaneTests(unittest.TestCase):
    def test_identity_is_independent_of_actor_scale_and_world_translation(self):
        a=np.eye(4);a[:3,:3]*=1.81;a[:3,3]=[3,4,5]
        b=a.copy();b[:3,3]=[6,8,9]
        m=bone_plane_matrix(a,b,{'rotation':[1.09,0,2.35]},[100,200],[110,190])
        np.testing.assert_allclose(m[:,:2],np.eye(2),atol=1e-12)
        np.testing.assert_allclose(m@np.array([100,200,1]),[110,190],atol=1e-12)
    def test_actual_projection_foreshortens_instead_of_resizing_to_toe_distance(self):
        a=np.eye(4);b=np.eye(4);b[:3,:3]=Rotation.from_euler('x',60,degrees=True).as_matrix()
        m=bone_plane_matrix(a,b,{'rotation':[0,0,0]},[0,0],[0,0])
        np.testing.assert_allclose(m[:,:2],np.diag([1,.5]),atol=1e-12)
    def test_reversed_or_edge_on_surface_requires_new_camera_art(self):
        a=np.eye(4)
        for angle in [90,150]:
            b=np.eye(4);b[:3,:3]=Rotation.from_euler('x',angle,degrees=True).as_matrix()
            with self.assertRaisesRegex(ValueError,'changes side'):bone_plane_matrix(a,b,{'rotation':[0,0,0]},[0,0],[0,0])
    def test_reflected_bone_matrix_is_rejected(self):
        a=np.eye(4);a[0,0]=-1
        with self.assertRaisesRegex(ValueError,'Reflected'):proper_rotation(a)
