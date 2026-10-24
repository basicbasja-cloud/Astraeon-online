import ast
import itertools
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from render_material_pose_guide import instrument,material_role,dominant_role


class MaterialPoseGuideTests(unittest.TestCase):
    def test_visible_hand_and_fingers_are_skin(self):
        for bone in ['hand_r','thumb_01_l','index_02_r','middle_03_l','pinky_01_r','ring_01_l']:self.assertEqual(material_role(bone,.8),'skin')

    def test_cuff_and_head_are_distinct_semantic_regions(self):
        self.assertEqual(material_role('lowerarm_r',1),'cuff');self.assertEqual(material_role('head',1.5),'head');self.assertEqual(material_role('neck_01',1.4),'skin')

    def test_boot_height_keeps_upper_calf_as_pants(self):
        self.assertEqual(material_role('calf_r',.39),'boots');self.assertEqual(material_role('calf_r',.41),'pants');self.assertEqual(material_role('foot_l',.1),'boots');self.assertEqual(material_role('thigh_l',.7),'pants')

    def test_material_ties_are_deterministic(self):
        for roles in itertools.permutations(['coat','skin','coat','skin']):self.assertEqual(dominant_role(list(roles)),'skin')
        self.assertEqual(dominant_role(['boots','boots','pants']),'boots')

    def test_unknown_face_role_is_rejected(self):
        with self.assertRaises(ValueError):dominant_role(['unknown'])

    def test_instrumentation_only_adds_one_material_callback(self):
        source=(Path(__file__).resolve().parents[2]/'tools/character_factory_v3/render_patch001_guides.py').read_text();original=ast.parse(source);result=instrument(source);main=next(n for n in result.body if isinstance(n,ast.FunctionDef)and n.name=='main');calls=[n for n in main.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='_assign_material_profile'];self.assertEqual(len(calls),1);main.body.remove(calls[0]);original.body=[n for n in original.body if not(isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and isinstance(n.test.left,ast.Name)and n.test.left.id=='__name__')];self.assertEqual(ast.dump(original,include_attributes=False),ast.dump(result,include_attributes=False))


if __name__=='__main__':unittest.main()
