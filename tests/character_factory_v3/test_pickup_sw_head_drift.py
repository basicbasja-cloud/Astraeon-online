import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import audit_pickup_sw_head_drift as audit
class HeadDriftTests(unittest.TestCase):
 def test_computes_both_unapproved_mask_variants(self):
  with tempfile.TemporaryDirectory() as tmp:
   report=audit.build(Path(tmp)/'audit');self.assertEqual(len(report['results']),4);self.assertEqual(report['frames'],[8,16]);self.assertFalse(report['runtime_admitted'])
   for variant in (0,2):
    entries={r['frame16_variant']:r['difference_runtime_px'] for r in report['results'] if r['mask_candidate']==variant};self.assertLess(entries['bounded'],entries['original'])
 def test_existing_output_is_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'audit';out.mkdir();(out/'keep').write_bytes(b'keep')
   with self.assertRaisesRegex(ValueError,'fresh output'):audit.build(out)
   self.assertEqual((out/'keep').read_bytes(),b'keep')
if __name__=='__main__':unittest.main()
