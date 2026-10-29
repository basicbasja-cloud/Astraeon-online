import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[2] / 'tools/character_factory_v3'
sys.path.insert(0, str(TOOLS))
import audit_pickup_sparse_head_drift as audit
import propose_pickup_sw06_head_repair as repair

class SparseHeadAuditTests(unittest.TestCase):
 def test_audit_has_nonadjacent_research_comparisons(self):
  result = audit.audit()
  self.assertEqual(result['status'], 'RESEARCH_NOT_APPROVED')
  self.assertEqual(len(result['comparisons']), 12)
  self.assertTrue(all(x['to_frame'] - x['from_frame'] == 2 for x in result['comparisons']))

 def test_repair_restores_module_settings_even_on_failure(self):
  old = repair.base.INITIAL, repair.base.DONOR, repair.base.ROI
  with patch.object(repair.base, 'build', side_effect=RuntimeError('stop')):
   with self.assertRaises(RuntimeError):
    repair.build(Path(tempfile.gettempdir()))
  self.assertEqual((repair.base.INITIAL, repair.base.DONOR, repair.base.ROI), old)

if __name__ == '__main__': unittest.main()
