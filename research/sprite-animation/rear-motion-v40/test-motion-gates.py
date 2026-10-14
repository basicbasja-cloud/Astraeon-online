import copy,importlib.util,json,unittest
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('motion',ROOT/'skills/modular-eight-direction-sprites/scripts/view-conditioned-motion.py');boots=m.boots
c=json.loads((P/'motion-contract.json').read_text());src=json.loads((P/'source/source.json').read_text());source=np.array([f['points']['head']['xy'] for f in src['frames']]);scale=c['guide_fidelity']['source_to_display_displacement_scale'];correct=(source-source[0])*scale+[188,186]
class MotionTests(unittest.TestCase):
    def test_known_guide_positive(self):self.assertTrue(m.fidelity(source,correct,scale,8)['pass_'])
    def test_positive_phase(self):self.assertTrue(m.phase(source,correct)['pass_'])
    def test_fitted_phase_hides_wrong_amplitude(self):
        bad=(correct-correct[0])*[.5,3]+correct[0]
        self.assertTrue(m.phase(source,bad)['pass_']);self.assertFalse(m.fidelity(source,bad,scale,8)['pass_'])
    def test_signed_phase_refuses_reflection(self):
        bad=correct.copy();bad[:,0]=2*bad[0,0]-bad[:,0];self.assertFalse(m.phase(source,bad)['pass_'])
    def test_unobservable_excursion_unknown(self):self.assertFalse(m.phase(source,np.tile([188,186],(8,1)))['pass_'])
    def test_actual_candidate_is_not_a_strict_pass(self):
        q=m.run(c,ROOT,P/'renders')['variants']['review'];self.assertTrue(q['phase_neck_support_pass']);self.assertFalse(q['metrics_pass']);self.assertGreater(q['guide_fidelity']['maximum_error_px'],26)
    def test_actual_before_keys_fail_phase(self):
        q=m.run(c,ROOT,P/'renders')['variants']['raw8'];self.assertFalse(q['projected_phase']['pass_'])
    def two(self):
        a=np.zeros((512,384,4),np.uint8);a[450:480,120:150,3]=255;a[440:470,220:250,3]=255;return a
    def test_two_separated_components(self):self.assertTrue(boots.observe(self.two(),[90,430,310,500])['known'])
    def test_crossing_boots_abstain(self):
        a=self.two();a[455:460,145:225,3]=255;self.assertFalse(boots.observe(a,[90,430,310,500])['known'])
    def test_missing_boot_abstain(self):
        a=self.two();a[:,200:]=0;self.assertFalse(boots.observe(a,[90,430,310,500])['known'])
    def test_clipped_support_abstain(self):
        a=self.two();a[480:501,120:150,3]=255;self.assertFalse(boots.observe(a,[90,430,310,500])['known'])
    def test_third_component_abstain(self):
        a=self.two();a[450:470,280:300,3]=255;self.assertFalse(boots.observe(a,[90,430,310,500])['known'])
    def test_actual_component_avoids_neighbor(self):
        row=c['variants']['review'][3];a=np.array(Image.open(ROOT/row['body']['path']).convert('RGBA'));o=boots.observe(a,[90,430,310,500]);self.assertTrue(o['known']);self.assertEqual(o['components'][1]['surface_xy'][0],223)
        self.assertEqual(m.neck.extrema(a,[215,435,305,479])[0],215) # old rectangle catches OTHER shoe
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MotionTests))
    (P/'motion-test-receipt.json').write_text(json.dumps(dict(tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),scope='Actual rendered negative case and synthetic positive/negative controls; passing software tests do not approve the rejected artwork.'),indent=2)+'\n');raise SystemExit(not r.wasSuccessful())
