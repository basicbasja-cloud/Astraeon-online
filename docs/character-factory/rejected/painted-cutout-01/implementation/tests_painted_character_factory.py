"""Contract tests for the new independent-painted-parts authoring factory."""
import copy
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from painted_character_factory import (DIRECTIONS, attachment_points, project,
                                       read_spec, require_coverage, sample_pose, variant_enabled)
from pack_painted_character_factory import adapt

FOLDER=ROOT/'authoring/characters/swordsman-production/fresh-2d/painted-rig-01'


class FactoryContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=read_spec(FOLDER/'rig.json')

    def test_missing_art_is_rejected_before_pack_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'sources'
            with self.assertRaisesRegex(ValueError,'Missing independent directional art'):
                adapt(self.spec,FOLDER/'motion-pilot',target,Path(tmp),'test-pilot',['Idle'])
            self.assertFalse(target.exists())

    def test_missing_motion_cannot_be_idle_fallback(self):
        with self.assertRaisesRegex(ValueError,'Missing authored motion: Death'):
            require_coverage(self.spec,['SE'],['Death'])

    def test_release_cannot_promote_unapproved_art(self):
        fixture=copy.deepcopy(self.spec)
        # Gate-only fixture; this must never be used to create a render/package.
        fixture['views']={d:{'ownerApproval':'PENDING'} for d in DIRECTIONS}
        with self.assertRaisesRegex(ValueError,'Owner visual approval is missing'):
            require_coverage(fixture,DIRECTIONS,['Idle'],release=True)

    def test_hilt_origin_follows_anatomical_right_hand_all_headings(self):
        for action,clip in self.spec['motions'].items():
            for d in DIRECTIONS:
                for i in range(len(clip['durations'])):
                    p=sample_pose(self.spec,d,action,i)
                    self.assertEqual(p['bones']['weapon'][0],p['sockets']['hand_R'])
                    self.assertEqual(p['sockets']['weapon'],p['sockets']['hand_R'])
                    self.assertEqual(p['sockets']['root'],[160,264])

    def test_forward_blade_axis_rotates_with_heading(self):
        p={d:sample_pose(self.spec,d,'Idle',0)['bones']['weapon'] for d in DIRECTIONS}
        self.assertLess(p['W'][1][0],p['W'][0][0])
        self.assertGreater(p['E'][1][0],p['E'][0][0])
        self.assertLess(p['NW'][1][0],p['NW'][0][0])
        self.assertGreater(p['NE'][1][0],p['NE'][0][0])
        self.assertAlmostEqual(p['N'][1][0],p['N'][0][0])

    def test_support_foot_stays_on_canonical_floor(self):
        for i in range(16):
            p=sample_pose(self.spec,'SE','Walk',i)['bodyJoints']
            self.assertAlmostEqual(min(p['sole_R'][2],p['sole_L'][2]),0.05)
            self.assertGreaterEqual(p['sole_R'][2],0.05)
            self.assertGreaterEqual(p['sole_L'][2],0.05)

    def test_projected_art_basis_has_no_reflection(self):
        # Local orientation: downward source y maps to positive bone y and
        # source right maps to negative local x, preserving handedness on stage.
        a={'rect':[0,0,10,20],'pivot':[0,0],'axisEnd':[0,20],'scale':1,'depth':0}
        points=attachment_points(a)
        self.assertEqual(points,[[0,20,0],[-10,20,0],[-10,0,0],[0,0,0]])
        for d in DIRECTIONS:
            a,b,c=project([0,0,0],d),project([1,0,0],d),project([0,1,0],d)
            area=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            self.assertAlmostEqual(area,-50.8**2*0.5,places=5)

    def test_skin_choice_never_selects_new_pose_data(self):
        attachments=self.spec['views']['SE']['attachments']
        for variant in self.spec['variants'].values():
            base=[a['id'] for a in attachments if a['slot'] in ('BaseBody','BodyHands') and variant_enabled(a,variant)]
            self.assertEqual(base,[a['id'] for a in attachments if a['slot'] in ('BaseBody','BodyHands')])
        for name in ('default','training'):
            weapons=[a['id'] for a in attachments if a['slot']=='Weapon' and variant_enabled(a,self.spec['variants'][name])]
            self.assertEqual(len(weapons),1)
        self.assertNotEqual(self.spec['variants']['default']['weapon'],self.spec['variants']['training']['weapon'])


if __name__=='__main__':
    unittest.main()
