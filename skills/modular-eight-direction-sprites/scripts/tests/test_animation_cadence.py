import importlib.util,unittest
from pathlib import Path
import numpy as np
from PIL import Image
loader=importlib.util.spec_from_file_location('cadence',Path(__file__).parents[1]/'animation-cadence.py');m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
ROOT=Path(__file__).resolve().parents[4]/'research/sprite-animation/leg-ownership-v16'
class CadenceTests(unittest.TestCase):
 def test_actual600ms_gif_has_quantized30_40_exposures(self):
  r=m.audit(ROOT/'attempt3/walk-ro-cadence.gif');self.assertEqual(r['frame_count'],16);self.assertEqual(r['duration_ms'],600);self.assertEqual(r['range_ms'],[30,40]);self.assertFalse(r['uniform_exposures'])
 def test_uniform800ms_files_retain_all16_exposures(self):
  for ext in ['gif','png','webp']:
   r=m.audit(ROOT/'uniform-review'/('walk-uniform-800ms.'+ext));self.assertEqual(r['frame_count'],16);self.assertEqual(r['duration_ms'],800);self.assertEqual(r['delays_ms'],[50]*16);self.assertFalse(r['anatomy_accepted'])
 def test_uniform_clock_does_not_change_visible_rgba_masters(self):
  for ext in ['png','webp']:
   with Image.open(ROOT/'uniform-review'/('walk-uniform-800ms.'+ext)) as im:
    for i in range(im.n_frames):
     im.seek(i);a=np.array(im.convert('RGBA'));b=np.array(Image.open(ROOT/'attempt3/frames'/f'{i:02}.png').convert('RGBA'));np.testing.assert_array_equal(a[:,:,3],b[:,:,3]);keep=b[:,:,3]>0;np.testing.assert_array_equal(a[keep],b[keep])
if __name__=='__main__':unittest.main()
