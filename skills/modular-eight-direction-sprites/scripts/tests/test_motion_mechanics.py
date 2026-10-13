import copy, importlib.util, tempfile, unittest, hashlib,json
from pathlib import Path
import numpy as np

SPEC=importlib.util.spec_from_file_location('motion_mechanics',Path(__file__).resolve().parents[1]/'motion-mechanics.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
def transform(deg=0,x=0):
    a=np.radians(deg);m=np.eye(4);m[:2,:2]=[[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]];m[0,3]=x;return m
def attack():
    local=transform(25,.12)
    return {'schema':'motion-mechanics-v1','action':'attack','frames':[
        {'time_ms':i*100,'hand_matrix_world':transform(i*60,i*.1).tolist(),
         'weapon_matrix_world':(transform(i*60,i*.1)@local).tolist()} for i in range(4)]}
def walk():
    frames=[]
    for i,lead in enumerate(['r','passing','l','passing']):
        xs=[35,10] if lead=='r' else [10,35] if lead=='l' else [20,20]
        feet={s:{'sole_xy':[xs[j],50],'ground_projection_xy':[xs[j],50],
                 'identity_reviewed':True,'contact':'stance'} for j,s in enumerate(['r','l'])}
        frames.append({'time_ms':i*100,'observed_lead':lead,'reference_lead':lead,'feet':feet,'travel_axis_xy':[1,0],'contact_state_reviewed':True,'root_xy':[20,30],'rest_lateral_separation_px':0})
    return {'schema':'motion-mechanics-v1','action':'walk','loop':True,'frames':frames}
class Mechanics(unittest.TestCase):
    def test_coupled_hand_and_weapon(self):
        r=M.audit(attack(),Path('.'));self.assertLess(r['metrics']['max_hand_local_weapon_matrix_delta'],1e-12);self.assertFalse(r['production_approved'])
    def test_prop_spins_while_hand_stays_fixed(self):
        c=attack()
        for f in c['frames']:f['hand_matrix_world']=np.eye(4).tolist()
        self.assertIn('Weapon moves inside the hand-local grip frame',M.audit(c,'.')['warnings'])
    def test_missing_axes_remain_unknown(self):
        c=attack()
        for f in c['frames']:f.pop('hand_matrix_world')
        self.assertEqual(M.audit(c,'.')['diagnostic_status'],'INCONCLUSIVE')
    def test_bad_projected_grip(self):
        c=attack();p={'palm':[0,0],'hilt':[20,0],'tip':[80,0],'wrist':[0,10],'knuckles':[0,0]}
        c['frames'][0].update(visible_points=p,reference_relative_blade_angle_deg=0,right_hand_identity_reviewed=True)
        r=M.audit(c,'.');self.assertTrue(any('gap' in x for x in r['warnings']));self.assertTrue(any('orientation' in x for x in r['warnings']))
    def test_hand_pivot_is_not_enough(self):
        c=attack();c['frames'][0]['visible_points']={'palm':[0,0],'hilt':[0,0],'tip':[50,0]}
        self.assertTrue(any('axis incomplete' in x for x in M.audit(c,'.')['unknown']))
    def test_hand_tail_mode_does_not_require_rendered_blade(self):
        c=attack();c['attack_representation']='hand_sweep_tail'
        for f in c['frames']:f['visible_points']={'palm':[0,0],'wrist':[0,10],'knuckles':[0,0]};f['right_hand_identity_reviewed']=True
        r=M.audit(c,'.');self.assertFalse(any('grip axis incomplete' in x for x in r['unknown']));self.assertEqual(r['metrics']['blade_angle_steps_deg'],[])
    def test_shared_socket_point_is_not_independent_grip_proof(self):
        c=attack();f=c['frames'][0];f.update(visible_points={'palm':[0,0],'hilt':[0,0],'tip':[80,0],'wrist':[0,10],'knuckles':[0,0]},palm_hilt_same_feature_calibration=True)
        r=M.audit(c,'.');self.assertEqual(r['metrics']['visible_hilt_palm_gaps_px'],[]);self.assertTrue(any('not independent' in x for x in r['unknown']))
    def test_projection_rule_uses_reference(self):
        c=attack();p={'palm':[0,0],'hilt':[0,0],'tip':[80,0],'wrist':[0,10],'knuckles':[0,0]}
        c['frames'][0].update(visible_points=p,reference_relative_blade_angle_deg=90,right_hand_identity_reviewed=True)
        self.assertFalse(any('orientation' in x for x in M.audit(c,'.')['warnings']))
    def test_walking_alternates(self):self.assertEqual(M.audit(walk(),'.')['metrics']['lead_switches'],2)
    def test_repeated_leading_leg_detected(self):
        c=walk()
        for f in c['frames']:f['observed_lead']='r'
        r=M.audit(c,'.');self.assertTrue(any('alternation' in x for x in r['warnings']));self.assertEqual(r['metrics']['reference_lead_mismatch_frames'],[2])
    def test_wrong_floor_lane_detected(self):
        c=walk();c['frames'][0]['feet']['r']['sole_xy'][1]-=20
        self.assertTrue(any('floor lane' in x for x in M.audit(c,'.')['warnings']))
    def test_cloth_labels_do_not_approve_owner(self):
        c=walk();c['frames'][0]['feet']['r']['identity_reviewed']=False
        self.assertTrue(any('hip-to-foot' in x for x in M.audit(c,'.')['unknown']))
    def test_fake_lead_labels_on_stationary_legs_fail(self):
        c=walk()
        for f in c['frames']:
            f['feet']['r']['sole_xy']=[35,50];f['feet']['l']['sole_xy']=[10,50]
        r=M.audit(c,'.');self.assertTrue(any('stationary' in x for x in r['warnings']));self.assertTrue(any('contradicts' in x for x in r['warnings']))
    def test_actor_translation_does_not_imitate_striding(self):
        c=walk()
        for i,f in enumerate(c['frames']):
            f['root_xy']=[i*20,30];f['feet']['r']['sole_xy']=[35+i*20,50];f['feet']['l']['sole_xy']=[10+i*20,50]
        self.assertTrue(any('stationary' in x for x in M.audit(c,'.')['warnings']))
    def test_known_rejection_overrides_clear_checks(self):
        c=walk();c['user_status']='USER_REJECTED_SLIDING';r=M.audit(c,'.');self.assertEqual(r['status'],'USER_REJECTED');self.assertFalse(r['production_approved'])
    def test_coupled_source_does_not_override_falling_rejection(self):
        c=attack();c['user_status']='USER_REJECTED_FALLING'
        for f in c['frames']:f['balance_review']='USER_REJECTED_FALLING'
        r=M.audit(c,'.');self.assertLess(r['metrics']['max_hand_local_weapon_matrix_delta'],1e-12);self.assertTrue(any('stance/balance' in x for x in r['warnings']));self.assertEqual(r['status'],'USER_REJECTED')
    def test_clock_must_be_strict(self):
        c=walk();c['frames'][1]['time_ms']=0
        with self.assertRaises(ValueError):M.audit(c,'.')
    def test_stale_pixels_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'frame.png';p.write_bytes(b'old');c=walk();c['frames'][0]['image']={'path':'frame.png','sha256':M.sha(p)};p.write_bytes(b'new')
            with self.assertRaises(ValueError):M.audit(c,tmp)
    def test_bound_feedback_cannot_be_cleared_by_relabel(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'frame.png';p.write_bytes(b'unchanged rejected pixels');bank=[{'sha256':M.sha(p)}]*4
            ledger=Path(tmp)/'feedback.json';ledger.write_text(json.dumps({'walk':{'E':{'status':'USER_REJECTED_SLIDING','frames':bank}}}))
            c=walk();c['user_status']='USER_ACCEPTED';c['feedback']={'path':'feedback.json','sha256':M.sha(ledger),'selector':['walk','E']}
            for f in c['frames']:f['image']={'path':'frame.png','sha256':M.sha(p)}
            self.assertEqual(M.audit(c,tmp)['status'],'USER_REJECTED')
    def test_nan_transforms_fail(self):
        c=attack();c['frames'][0]['hand_matrix_world'][0][0]=float('nan')
        with self.assertRaises(ValueError):M.audit(c,'.')
if __name__=='__main__':unittest.main()
