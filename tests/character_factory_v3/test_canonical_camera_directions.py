import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'tools/character_factory_v3/render_canonical_rig_pilot.py'


class CanonicalCameraTests(unittest.TestCase):
    def constants(self):
        result={}
        for node in ast.parse(SOURCE.read_text()).body:
            if isinstance(node,ast.Assign):
                for target in node.targets:
                    if isinstance(target,ast.Name) and target.id in ['YAWS','ATTACK_DIRECTIONS']:
                        result[target.id]=ast.literal_eval(node.value)
        return result

    def test_all_eight_real_cameras_are_available(self):
        cameras=self.constants()['YAWS']
        self.assertEqual(set(cameras),{'S','SW','W','NW','N','NE','E','SE'})
        self.assertEqual(len({v%360 for v in cameras.values()}),8)

    def test_existing_four_diagonal_angles_are_preserved(self):
        cameras=self.constants()['YAWS']
        for name,angle in {'SW':-45,'NW':-135,'NE':135,'SE':45}.items():
            self.assertEqual(cameras[name],angle)

    def test_attack_and_cast_default_still_has_four_views(self):
        self.assertEqual(self.constants()['ATTACK_DIRECTIONS'],['SW','NW','NE','SE'])
        tree=ast.parse(SOURCE.read_text())
        call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
                  and n.func.attr=='add_argument' and n.args and isinstance(n.args[0],ast.Constant)
                  and n.args[0].value=='--directions')
        default=next(k.value for k in call.keywords if k.arg=='default')
        self.assertEqual(ast.unparse(default),'ATTACK_DIRECTIONS')

    def test_material_replay_uses_the_captured_implementation(self):
        tree=ast.parse((ROOT/'tools/character_factory_v3/render_canonical_material_guide.py').read_text())
        renderer=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign)
                      and any(isinstance(t,ast.Name) and t.id=='renderer' for t in n.targets))
        self.assertEqual(ast.unparse(renderer),"args.canonical_guide / 'renderer-source.py'")


if __name__=='__main__':
    unittest.main()
