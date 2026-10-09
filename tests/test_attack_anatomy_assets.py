import hashlib
import json
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'authoring/characters/builds/swordsman-basicattack-anatomy-v1'


class AttackAnatomyAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads((ROOT / 'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json').read_text())
        cls.pack = json.loads((ROOT / 'authoring/characters/appearance/swordsman-basicattack-anatomy/appearance-pack.json').read_text())
        cls.receipt = json.loads((BUILD / 'packaging-receipt.json').read_text())
        cls.edits = json.loads((BUILD / 'candidate/normalization-receipt.json').read_text())['frames']
        cls.before = np.asarray(Image.open(ROOT / cls.old['atlases']['body-basicattack']['file']).convert('RGBA'))
        cls.after = np.asarray(Image.open(ROOT / cls.pack['atlases']['body-basicattack']['file']).convert('RGBA'))

    def test_55_authored_patches_preserve_every_pixel_outside_limb_masks(self):
        edited = {(e['direction'], e['frame']) for e in self.edits}
        self.assertEqual(len(edited), 55)
        for row, direction in enumerate(self.pack['bodyContract']['directions']):
            for frame in range(16):
                y, x = row*320, frame*320
                before = self.before[y:y+320, x:x+320]
                after = self.after[y:y+320, x:x+320]
                if (direction, frame) not in edited:
                    self.assertTrue(np.array_equal(before, after), (direction, frame))
                else:
                    mask = np.asarray(Image.open(BUILD / 'candidate' / f'{direction}-{frame:02}-mask.png')) > 0
                    self.assertTrue(np.array_equal(before[~mask], after[~mask]), (direction, frame))
                    self.assertGreater(np.count_nonzero(before != after), 100, (direction, frame))

    def test_independent_head_and_all_non_attack_layers_remain_original(self):
        for part in ['swordsman-head', 'hair-a', 'hair-b', 'offhand', 'headgear', 'garment']:
            self.assertEqual(self.old['parts'][part], self.pack['parts'][part], part)
        for action in ['Idle', 'Walk']:
            self.assertEqual(self.old['bodyContract']['anchorRegistration'][action], self.pack['bodyContract']['anchorRegistration'][action])
            for part in self.pack['parts']:
                self.assertEqual(self.old['parts'][part]['timelines'].get(action), self.pack['parts'][part]['timelines'].get(action))
        for atlas, metadata in self.old['atlases'].items():
            if atlas not in ['body-basicattack', 'royal-basicattack']:
                self.assertEqual(metadata, self.pack['atlases'][atlas])

    def test_body_patch_cannot_admit_pixels_at_original_head_silhouette(self):
        heads = Image.open(ROOT / self.old['atlases']['head-basicattack']['file']).convert('RGBA')
        for e in self.edits:
            direction, frame = e['direction'], e['frame']
            ref = self.old['parts']['swordsman-head']['timelines']['BasicAttack'][direction]['frames'][frame]['layers']['HeadBase']
            x, y, w, h = ref['rect']
            mask = Image.new('L', (320, 320))
            mask.paste(heads.crop((x, y, x+w, y+h)).getchannel('A'), tuple(ref['trim']['offset']))
            arm_mask = np.asarray(Image.open(BUILD / 'candidate' / f'{direction}-{frame:02}-mask.png'))
            self.assertFalse(np.any(arm_mask[np.asarray(mask) > 0]), (direction, frame))

    def test_all_registered_palms_lie_on_opaque_body_pixels(self):
        for e in self.receipt['hands']:
            row = self.pack['bodyContract']['directions'].index(e['direction'])
            x, y = (round(v) for v in e['grip'])
            self.assertGreater(self.after[row*320+y, e['frame']*320+x, 3], 200, (e['direction'], e['frame']))

    def test_costume_proof_retains_the_same_anatomical_alpha_and_untouched_royal_pixels(self):
        royal = np.asarray(Image.open(ROOT / self.pack['atlases']['royal-basicattack']['file']).convert('RGBA'))
        old_royal = np.asarray(Image.open(ROOT / self.old['atlases']['royal-basicattack']['file']).convert('RGBA'))
        self.assertTrue(np.array_equal(royal[:, :, 3], self.after[:, :, 3]))
        unchanged = np.all(self.before == self.after, axis=2)
        self.assertTrue(np.array_equal(royal[unchanged], old_royal[unchanged]))

    def test_owned_weapon_openings_preserve_guard_blade_pommel_and_idle_walk_assets(self):
        for weapon in ['weapon-a', 'weapon-b']:
            before = np.asarray(Image.open(ROOT / self.old['atlases'][weapon]['file']).convert('RGBA'))
            after = np.asarray(Image.open(ROOT / self.pack['atlases'][weapon+'-attack-grip']['file']).convert('RGBA'))
            opening = np.asarray(Image.open(BUILD / (weapon+'-grip-opening-mask.png'))) > 0
            self.assertTrue(np.array_equal(before[~opening], after[~opening]))
            self.assertTrue(np.all(after[opening] == 0))
            for row in range(8):
                self.assertEqual(after[row*128+98, 24, 3], 0)
            self.assertEqual(self.old['atlases'][weapon], self.pack['atlases'][weapon])

    def test_attack_arm_reuse_shortcuts_have_distinct_new_paintings(self):
        for direction, frame, source in [('SW', 7, 8), ('NW', 7, 8), ('W', 10, 11), ('W', 14, 13), ('W', 15, 13)]:
            row = self.pack['bodyContract']['directions'].index(direction)
            a = self.after[row*320:(row+1)*320, frame*320:(frame+1)*320]
            b = self.after[row*320:(row+1)*320, source*320:(source+1)*320]
            self.assertFalse(np.array_equal(a, b), (direction, frame, source))

    def test_receipts_protect_motion_and_record_pending_owner_review(self):
        sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        previous = json.loads((ROOT / 'authoring/characters/builds/swordsman-registration-v1/salvage-receipt.json').read_text())
        self.assertEqual(self.receipt['motionTemplateSHA256'], previous['motionTemplateSHA256'])
        for atlas, metadata in self.pack['atlases'].items():
            self.assertEqual(sha(ROOT / metadata['file']), self.receipt['runtimeAtlases'][atlas])
        self.assertEqual(self.receipt['ownerVisualApproval'], 'PENDING')
        self.assertEqual(self.pack['status'], 'REQUIRES_OWNER_VISUAL_REVIEW')


if __name__ == '__main__':
    unittest.main()
