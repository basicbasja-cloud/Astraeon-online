import copy,importlib.util,json,unittest
from pathlib import Path
from PIL import Image
import numpy as np
loader=importlib.util.spec_from_file_location('panel_gutters',Path(__file__).parents[2]/'studies/walk-test/pack-panel-grid.py');m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
ROOT=Path(__file__).resolve().parents[4]
class PanelGutterTests(unittest.TestCase):
 def test_real_extended_cape_requires_actual_empty_column_gutters(self):
  p=ROOT/'research/sprite-animation/leg-ownership-v16/evidence/attempt3-row-registration.json';s=json.loads(p.read_text());a=np.array(Image.open(s['raw']).convert('RGBA'))[:,:,3];self.assertLessEqual(max(m.validate_panel_cuts(a,s)),64)
  bad=copy.deepcopy(s);bad.pop('raw_column_panel_bounds',None)
  with self.assertRaisesRegex(ValueError,'foreground'):m.validate_panel_cuts(a,bad)
 def test_one_foreground_pixel_at_declared_gutter_is_rejected(self):
  p=ROOT/'research/sprite-animation/leg-ownership-v16/evidence/attempt3-row-registration.json';s=json.loads(p.read_text());a=np.array(Image.open(s['raw']).convert('RGBA'))[:,:,3];a[326,150]=255
  with self.assertRaisesRegex(ValueError,'foreground'):m.validate_panel_cuts(a,s)
if __name__=='__main__':unittest.main()
