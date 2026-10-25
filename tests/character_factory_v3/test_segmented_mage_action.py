import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from render_segmented_mage_action import segment_matrix,palm_matrix,make_parts,rigid_head_matrix
from build_occluded_underlays import composite

class SegmentedMageTests(unittest.TestCase):
    def test_segment_transport_preserves_endpoints_and_width(self):
        source=np.array([[0,0],[10,0]],float);target=np.array([[3,4],[3,24]],float)
        matrix=segment_matrix(source,target)
        np.testing.assert_allclose(source@matrix[:,:2].T+matrix[:,2],target,atol=1e-12)
        np.testing.assert_allclose(matrix[:,:2]@[0,1],[-1,0],atol=1e-12)
    def test_three_point_palm_follows_captured_plane(self):
        source=np.array([[0,0],[10,0],[0,10]],float);target=np.array([[5,6],[25,6],[5,16]],float)
        matrix=palm_matrix(source,target)
        np.testing.assert_allclose(source@matrix[:,:2].T+matrix[:,2],target,atol=1e-12)
    def test_palm_visible_side_flip_requires_another_authored_hand(self):
        source=[[0,0],[10,0],[0,10]]
        with self.assertRaisesRegex(ValueError,'changes visible side'):
            palm_matrix(source,[[0,0],[-10,0],[0,10]])
    def test_joint_underlaps_do_not_double_semtransparent_edges(self):
        body=Image.new('RGBA',(32,32));body.putpixel((9,10),(120,80,40,128));body.putpixel((10,10),(120,80,40,255))
        landmarks={'UpperArm.L':[12,10],'Forearm.L':[6,10],'Hand.L':[2,10],
                   'UpperArm.R':[20,10],'Forearm.R':[25,10],'Hand.R':[28,10]}
        recipe={'arm_polygons':{'L':[[0,0],[15,0],[15,31],[0,31]],'R':[[20,0],[31,0],[31,31],[20,31]]},
                'art_joints':landmarks,'joint_underlap_px':2,'shoulder_caps_radius_px':12}
        parts=make_parts(body,recipe,landmarks)
        self.assertEqual(composite(list(parts.values())).tobytes(),body.tobytes())

    def test_rigid_head_transport_never_changes_head_scale(self):
        source=np.array([[10,30],[10,10]],float);target=np.array([[13,34],[15,12]],float)
        matrix=rigid_head_matrix(source,target)
        np.testing.assert_allclose(matrix[:,:2].T@matrix[:,:2],np.eye(2),atol=1e-12)
        np.testing.assert_allclose(matrix[:,:2]@source[1]+matrix[:,2],target[1],atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(matrix[:,:2]),1)
    def test_degenerate_head_axis_requires_another_source(self):
        with self.assertRaisesRegex(ValueError,'head axis'):
            rigid_head_matrix([[0,0],[1,0]],[[0,0],[0,10]])
