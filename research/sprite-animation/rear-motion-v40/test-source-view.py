import copy, importlib.util, json, unittest
from pathlib import Path
P=Path(__file__).resolve().parent; ROOT=P.parents[2]
spec=importlib.util.spec_from_file_location('view_audit',ROOT/'skills/modular-eight-direction-sprites/scripts/physical-view-source-audit.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=json.loads((P.parent/'pickup-pilot-v31/source/source.json').read_text())
current=json.loads((P/'source/source.json').read_text())
class SourceViewTests(unittest.TestCase):
    def test_actual_camera_and_world(self):self.assertTrue(m.audit(old,current)['source_view_pass'])
    def test_mirrored_raster_is_not_camera(self):
        d=copy.deepcopy(current)
        for f in d['frames']:
            for p in f['points'].values():p['xy'][0]=384-p['xy'][0]
        self.assertFalse(m.audit(old,d)['checks']['independent_projection_matches'])
    def test_changed_world_joint(self):
        d=copy.deepcopy(current);d['frames'][3]['points']['left.knee']['world_xyz'][0]+=.1
        self.assertFalse(m.audit(old,d)['checks']['world_motion_unchanged'])
    def test_owner_relabel(self):
        d=copy.deepcopy(current);pts=d['frames'][2]['points'];pts['left.wrist'],pts['right.wrist']=pts['right.wrist'],pts['left.wrist']
        self.assertFalse(m.audit(old,d)['checks']['world_motion_unchanged'])
    def test_clock_edit(self):
        d=copy.deepcopy(current);d['frames'][4]['source_time_seconds']+=.05
        self.assertFalse(m.audit(old,d)['checks']['same_clock'])
    def test_duplicate_final_exposure(self):
        d=copy.deepcopy(current);d['frames'].append(d['frames'][-1])
        self.assertFalse(m.audit(old,d)['checks']['eight_samples'])
    def test_same_camera(self):self.assertFalse(m.audit(old,old)['checks']['different_physical_camera'])
    def test_wrong_action(self):
        d=copy.deepcopy(current);d['clip']='Attack'
        self.assertFalse(m.audit(old,d)['checks']['same_clip'])
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceViewTests))
    (P/'source-test-receipt.json').write_text(json.dumps(dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),scope='Actual source and deliberately corrupted negative controls. No rendered-art accuracy claim.'),indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
