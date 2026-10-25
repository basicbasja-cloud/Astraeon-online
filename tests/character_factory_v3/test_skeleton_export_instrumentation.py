import ast
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / 'tools/character_factory_v3/export_evaluated_guide_skeleton.py'
spec = importlib.util.spec_from_file_location('skeleton_export', MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SkeletonInstrumentationTests(unittest.TestCase):
    def test_existing_renderer_exports_once_without_rendering(self):
        path = MODULE.with_name('render_patch001_guides.py')
        original = path.read_bytes()
        tree = module.instrument(original.decode())
        calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertEqual(calls.count('_record_skeleton'), 1)
        self.assertNotIn('bpy.ops.render.render', calls)
        self.assertGreaterEqual(calls.count('_existing_image'), 1)
        self.assertEqual(path.read_bytes(), original)

    def test_missing_boundary_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'boundaries differ'):
            module.instrument('def main():\n    pass\n')

    def test_duplicate_skeleton_boundary_fails_closed(self):
        with self.assertRaises(ValueError):
            module.instrument('def main():\n    bones = {}\n    bones = {}\n    bpy.ops.render.render()\n    Image.open(path)\n')

    def test_source_cli_guard_is_removed(self):
        tree = module.instrument(MODULE.with_name('render_patch001_guides.py').read_text())
        self.assertFalse(any(isinstance(n, ast.If) for n in tree.body))


if __name__ == '__main__':
    unittest.main()
