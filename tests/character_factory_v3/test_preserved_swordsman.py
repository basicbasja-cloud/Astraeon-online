import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from register_preserved_swordsman import camera_mapping, root_screen_delta, transform, refine_blade_ownership
from review_preserved_swordsman import clean_frame


class PreservedSwordsmanTests(unittest.TestCase):
    def test_action_cameras_map_to_one_root_with_one_isotropic_scale(self):
        target=np.array([384.,550.4])
        for ortho,root in [(3.4,[256,369.7185]),(3.547841787,[256,422.4])]:
            scale,offset=camera_mapping(ortho,root,5.325,target)
            np.testing.assert_allclose(np.array(root)*scale+offset,target)
            self.assertAlmostEqual(scale,(768/5.325)/(512/ortho))

    def test_source_root_extraction_uses_camera_axes_not_painted_bounds(self):
        rotation=[1.093904495,0.,.7853983]
        delta=root_screen_delta([0.,-.3020556,0.],rotation,512/3.547841787)
        scale,offset=camera_mapping(3.547841787,[256,422.4],5.325,[384,550.4],root_delta=delta)
        np.testing.assert_allclose(scale*(np.array([256,422.4])+delta)+offset,[384,550.4])
        self.assertLess(delta[0],0)
        self.assertGreater(delta[1],0)

    def test_identity_transform_preserves_pixel_placement(self):
        source=Image.new('RGBA',(32,32));source.putpixel((5,7),(30,20,10,255))
        result=transform(source,1.,np.array([4.,2.]),size=40)
        self.assertEqual(result.getbbox(),(9,9,10,10))

    def test_cleaned_visible_layers_recompose_and_source_is_unchanged(self):
        master=Image.new('RGBA',(16,16));master.paste((30,20,10,255),(3,3,13,13))
        master.paste((165,161,157,255),(3,2,13,3))
        parts={r:Image.new('RGBA',master.size)for r in ['BodyCostume','HeadHair','Weapon']}
        parts['BodyCostume']=master.copy();before=master.tobytes()
        cleaned,result,receipt=clean_frame(master,parts)
        actual=Image.new('RGBA',master.size)
        for im in result.values():actual.alpha_composite(im)
        self.assertEqual(actual.tobytes(),cleaned.tobytes())
        self.assertEqual(master.tobytes(),before)
        self.assertEqual(receipt['protected_interior_pixel_changes'],0)

    def test_overlapping_baseline_parts_are_not_silently_partitioned(self):
        master=Image.new('RGBA',(16,16),(30,20,10,255))
        parts={'BodyCostume':master.copy(),'HeadHair':master.copy(),'Weapon':Image.new('RGBA',master.size)}
        with self.assertRaisesRegex(ValueError,'overlap'):clean_frame(master,parts)


    def test_blade_outline_refinement_protects_grip_and_head(self):
        master=Image.new('RGBA',(64,64),(60,40,20,255))
        body=np.full((64,64),255,dtype=np.uint8);head=np.zeros_like(body);weapon=np.zeros_like(body)
        weapon[30:33,10:41]=255;body[weapon>0]=0;head[29,20]=255;body[29,20]=0
        ann={'weapon_tip':[10,31],'weapon_guard':[40,31],'weapon_grip':[44,31]}
        result,count=refine_blade_ownership(master,[Image.fromarray(x)for x in [body,head,weapon]],ann)
        self.assertGreater(count,0)
        self.assertEqual(np.array(result[2])[29,20],0)
        self.assertEqual(np.array(result[0])[29,40],255)
        self.assertEqual(np.array(result[2])[29,10],255)
        np.testing.assert_array_equal(sum(np.array(x,dtype=np.uint16)for x in result),255)


if __name__=='__main__':unittest.main()
