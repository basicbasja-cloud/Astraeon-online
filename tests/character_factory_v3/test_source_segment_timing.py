import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from source_segment_timing import source_timing
class SourceTimingTests(unittest.TestCase):
 def data(self):
  return {'job':{'source_actions':['A','B'],'source_ranges':{'A':[0,10],'B':[0,20]}},'views':{'SW':{'frames':[{'action':'A','source_frame':0},{'action':'A','source_frame':9},{'action':'B','source_frame':1},{'action':'B','source_frame':20}]}}}
 def test_action_boundary_uses_native_time(self):
  r=source_timing(self.data(),'SW',fps=10);self.assertEqual(r['source_times_ms'],[0,900,1100,3000]);self.assertEqual(r['gif_durations_ms'],[900,200,1900,200])
 def test_real_mage_timeline(self):
  p=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/ebac492fbc20b608880c/manifest.json';r=source_timing(json.loads(p.read_text()),'SW');self.assertEqual(len(r['gif_durations_ms']),24);self.assertAlmostEqual(r['source_motion_duration_ms'],40/24*1000);self.assertLess(abs(sum(r['gif_durations_ms'][:-1])-r['source_times_ms'][-1]),6)
 def test_unknown_source_interval_cannot_guess(self):
  d=self.data();del d['job']['source_ranges']['B']
  with self.assertRaisesRegex(ValueError,'Explicit'):source_timing(d,'SW')
 def test_transition_cannot_be_mistimed(self):
  d=self.data();d['views']['SW']['frames'][0]['transition_from']='Idle'
  with self.assertRaisesRegex(ValueError,'transitions'):source_timing(d,'SW')
