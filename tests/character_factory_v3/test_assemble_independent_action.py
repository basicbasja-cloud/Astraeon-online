import sys
from pathlib import Path
import unittest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from assemble_independent_action import assemble,BODY_ORDER,PUBLIC_ORDER
from build_occluded_underlays import composite


class PublicRoleAssemblyTests(unittest.TestCase):
    def make_parts(self):
        return {name:Image.new('RGBA',(8,8))for name in [*BODY_ORDER,'Weapon','HeadHair']}
    def test_hidden_body_and_whole_weapon_are_retained(self):
        parts=self.make_parts()
        parts['Weapon'].putpixel((3,3),(100,60,20,255))
        parts['Torso'].putpixel((3,3),(20,30,70,255))
        parts['HeadHair'].putpixel((3,3),(90,30,20,255))
        original=composite([parts['Weapon'],parts['Torso'],parts['HeadHair']])
        public,master,diff=assemble(parts,original)
        self.assertEqual(diff,0);self.assertEqual(master.tobytes(),original.tobytes())
        self.assertEqual(public['BodyCostume'].getpixel((3,3)),(20,30,70,255))
        self.assertEqual(public['Weapon'].getpixel((3,3)),(100,60,20,255))
    def test_forearm_over_head_cannot_be_silently_collapsed(self):
        parts=self.make_parts()
        parts['ForearmL'].putpixel((3,3),(20,30,70,255))
        parts['HeadHair'].putpixel((3,3),(90,30,20,255))
        original=composite([parts['HeadHair'],parts['ForearmL']])
        with self.assertRaisesRegex(ValueError,'occlusion'):assemble(parts,original)
