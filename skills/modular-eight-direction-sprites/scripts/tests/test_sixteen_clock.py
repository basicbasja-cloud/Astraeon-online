import json,unittest
from pathlib import Path
import numpy as np
from PIL import Image
class SixteenClockTests(unittest.TestCase):
 def test_actual16_frames_use_fractional_source_times_and_same600ms_cycle(self):
  root=Path(__file__).resolve().parents[4]/'research/sprite-animation/ground-walk-sixteen-v15';m=json.loads((root/'candidate/manifest.json').read_text())
  self.assertEqual(len(m['frames']),16);self.assertEqual(m['frames'][1]['source_index'],2.5);self.assertEqual(sum(m['ro_reference_frame_delays_ms']),600);self.assertEqual(set(m['ro_reference_frame_delays_ms']),{37,38});self.assertEqual(sum(m['gif_delays_ms']),600)
  for extension in ['png','webp','gif']:
   with Image.open(root/'candidate'/('walk-ro-cadence.'+extension)) as im:self.assertEqual(im.n_frames,16)
 def test_8_control_is_exact_even_frames_of_same_art_bank(self):
  root=Path(__file__).resolve().parents[4]/'research/sprite-animation/ground-walk-sixteen-v15'
  for i in range(8):
   with Image.open(root/'candidate/frames'/f'{i*2:02}.png') as a,Image.open(root/'eight-subset-control/frames'/f'{i:02}.png') as b:np.testing.assert_array_equal(np.array(a),np.array(b))
  m=json.loads((root/'eight-subset-control/manifest.json').read_text());self.assertEqual(sum(m['ro_reference_frame_delays_ms']),600)
if __name__=='__main__':unittest.main()
