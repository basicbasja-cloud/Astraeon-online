import hashlib
import json
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'authoring/characters/true-modular/swordsman-male-v2'
M=json.loads((SRC/'source-manifest.json').read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def opaque_bounds(im):
    y,x=np.where(np.asarray(im)[:,:,3]>128)
    return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]

class ModularSouthSources(unittest.TestCase):
    def test_actual_pngs_have_shared_rgba_canvas_and_clear_crop_margins(self):
        for p in M['parts'].values():
            for r in p['layers'].values():
                path=ROOT/r['file']
                self.assertEqual(path.read_bytes()[:8],b'\x89PNG\r\n\x1a\n')
                with Image.open(path) as im:
                    self.assertEqual(im.mode,'RGBA');self.assertEqual(im.size,(320,320))
                    a=np.asarray(im)[:,:,3]
                    self.assertFalse((a[:2,:]>128).any() or (a[-2:,:]>128).any() or (a[:,:2]>128).any() or (a[:,-2:]>128).any())

    def test_body_head_face_outfit_remain_different_immutable_source_bytes(self):
        paths=[ROOT/next(iter(M['parts'][n]['layers'].values()))['rawSource'] for n in ['bodycore','headbase','face','outfit-a']]
        self.assertEqual(len(set(paths)),4);self.assertEqual(len({digest(p) for p in paths}),4)
        for p in M['parts'].values():
            for r in p['layers'].values():
                self.assertEqual(digest(ROOT/r['rawSource']),r['rawSHA256'])
                self.assertEqual(digest(ROOT/r['file']),r['rasterSHA256'])

    def test_normalization_does_not_conceal_failed_face_or_outfit_registration(self):
        with Image.open(ROOT/M['parts']['headbase']['layers']['HeadBase']['file']) as h,Image.open(ROOT/M['parts']['face']['layers']['Face']['file']) as f,Image.open(ROOT/M['parts']['outfit-a']['layers']['OutfitFront']['file']) as o:
            hb,fb,ob=opaque_bounds(h),opaque_bounds(f),opaque_bounds(o)
        # These are deliberate failure evidence, not art approval assertions.
        self.assertGreater(fb[1],hb[1]+35)
        self.assertLess(ob[1],128)
        report=json.loads((ROOT/'docs/review/character-true-modular-v2/visual-gate.json').read_text())
        self.assertEqual(report['southGate'],'VISUAL_FAIL')
        self.assertFalse(report['checks']['faceWithinHeadZone'])
        self.assertFalse(report['checks']['outfitTopOutsideHeadZone'])

    def test_missing_hair_is_not_replaced_by_empty_pngs_or_v1_monolithic_body(self):
        self.assertIsNone(M['defaultParts']['Hair']);self.assertEqual(M['missingComponents'],['HairBack','HairFront'])
        files={r['rawSource'] for p in M['parts'].values() for r in p['layers'].values()}
        self.assertFalse(any('/bodies/swordsman-male-default/' in s for s in files))
        self.assertFalse((ROOT/'assets/characters/swordsman-true-modular-v2/hairback.png').exists())
        self.assertFalse((ROOT/'assets/characters/swordsman-true-modular-v2/hairfront.png').exists())

    def test_identity_authority_and_three_action_motion_remain_pinned(self):
        self.assertEqual(digest(ROOT/'authoring/characters/gait-rig-v50/approved-warrior-seed.png'),'750ffe25056760c6ab97c3e66a3488d15aec4c875e573d9a8cef65c8f0437e05')
        self.assertEqual(M['availablePoses'],['Idle/S/key0'])
        self.assertEqual(M['directionOrder'],['S','SW','W','NW','N','NE','E','SE'])
        t=json.loads((ROOT/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json').read_text())
        self.assertEqual(list(t['actions']),['Idle','Walk','BasicAttack'])
        self.assertEqual(t['actions']['Walk']['directions']['S']['totalDurationMs'],600)

if __name__=='__main__':unittest.main()
