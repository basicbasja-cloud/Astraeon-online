import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from propose_source_cutouts import nearest_visible,retain_soft_edges,source_prompts


class SourceCutoutProposalTests(unittest.TestCase):
    def test_nearest_prompt_uses_only_visible_allowed_pixels(self):
        pixels=np.zeros((16,16,4),dtype=np.uint8);pixels[5,5]=[250,250,250,255];pixels[10,10]=[250,250,250,255]
        scope=np.zeros((16,16),bool);scope[10,10]=True
        self.assertEqual(nearest_visible(pixels,[5,5],scope),[10,10])
        with self.assertRaises(ValueError):nearest_visible(pixels,[5,5],~(pixels[:,:,3]>0))

    def test_edge_ownership_is_bounded_and_retains_source_pixels(self):
        pixels=np.zeros((16,16,4),dtype=np.uint8);pixels[5,5]=[230,230,230,255];pixels[5,8]=[245,245,245,20];pixels[5,9]=[245,245,245,20];pixels[6,5]=[160,100,30,255]
        original=pixels.copy();mask=np.zeros((16,16),bool);mask[5,5]=True
        result=retain_soft_edges(pixels,mask)
        self.assertTrue(result[5,8]);self.assertFalse(result[5,9]);self.assertFalse(result[6,5]);np.testing.assert_array_equal(pixels,original)

    def test_foreshortened_weapon_requires_manual_annotation(self):
        pixels=np.ones((128,128,4),dtype=np.uint8)*255
        frame={'landmarks':{'head':[64,64],'hand_l':[10,80],'hand_r':[90,80]},'weapon_guide':{'grip':[90,80],'tip':[92,82]}}
        with self.assertRaisesRegex(ValueError,'foreshortened'):source_prompts(pixels,frame,1.)

    def test_occluded_joint_projection_is_not_a_visible_negative_prompt(self):
        pixels=np.full((512,512,4),200,dtype=np.uint8);pixels[:,:,3]=255
        frame={'landmarks':{'head':[180,100],'hand_l':[180,72],'hand_r':[200,300]},'weapon_guide':{'grip':[200,300],'tip':[200,100]}}
        prompts=source_prompts(pixels,frame,1.)
        self.assertEqual(len(prompts['HeadHair']['negative']),1);self.assertEqual(len(prompts['Weapon']['negative']),1)
        self.assertNotIn(frame['landmarks']['hand_r'],prompts['Weapon']['negative'])


if __name__=='__main__':unittest.main()
