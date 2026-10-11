"""Integration checks against the delivered native-derived sprite package.

Checks actual strips, grip projection and removal behavior rather than only
asserting that the exporter emitted its own metadata. Run after the full pack.
"""
import hashlib,importlib.util,json,unittest
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/swordsman-production/fantasy-base-01'
spec=importlib.util.spec_from_file_location('sprite_packer',ROOT/'tools/pack-character-sprites.py')
packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class FantasySpritePackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package=read('package.json');cls.audit=read('factory/source-audit.json');cls.validation=read('validation.json')
        cls.clips={c['name']:c for c in cls.package['clips']}
        cls.results={'nativeSHA256':cls.package['nativeSHA256'],'capeRemoval':[],'gripSamples':[]}

    def test_input_and_native_receipts(self):
        recipe=read('factory/recipe.json')
        self.assertEqual(sha(Path(recipe['sourceArchive'])),recipe['sourceArchiveSHA256'])
        self.assertEqual(sha(ROOT/recipe['approvedConcept']),recipe['approvedConceptSHA256'])
        self.assertEqual(sha(ROOT/recipe['productionNative']),self.package['nativeSHA256'])
        self.assertEqual(self.audit['nativeSHA256'],self.package['nativeSHA256'])
        self.assertEqual(self.audit['technicalVerdict'],'PASS');self.assertEqual(self.validation['technicalVerdict'],'PASS')
        self.assertFalse(self.package['ownerApproved']);self.assertFalse(self.package['runtimeAdmitted'])

    def test_complete_action_timing_and_dimensions(self):
        blueprint=json.loads((ROOT/'authoring/characters/true-modular/swordsman/male/blueprint.json').read_text(encoding='utf-8-sig'))
        matrix=json.loads((ROOT/'docs/character-factory/new-production-matrix.json').read_text())
        expected={c['action'] for c in matrix['actions'] if c['swordsmanContract']!='excluded'}
        self.assertEqual(set(self.clips),expected);self.assertEqual(self.package['missingActions'],[])
        self.assertEqual(self.package['requiredFramePositionsRendered'],1392)
        self.assertEqual(self.package['totalFramePositionsRendered'],1456)
        for name,clip in self.clips.items():
            timing=blueprint['clips'][name]
            self.assertEqual(clip['frames'],timing['frames']);self.assertEqual(clip['durationsMs'],timing['durationsMs']);self.assertEqual(clip['loop'],timing['loop'])
            self.assertEqual(clip['directions'],['S','SW','W','NW','N','NE','E','SE'])
            for direction,paths in clip['strips'].items():
                self.assertEqual(set(paths),set(packer.MODULES+['Composite','NativeReference']+['Depth-'+m for m in packer.MODULES]))
                for module,path in paths.items():
                    with Image.open(OUT/path) as image:
                        self.assertEqual(image.size,(320*clip['frames'],320))
                        self.assertEqual(image.mode,'RGB' if module.startswith('Depth-') else 'RGBA')

    def test_real_cape_removal_reveals_concealed_body(self):
        clip=self.clips['Idle']
        for direction in ['NW','N']:
            paths=clip['strips'][direction]
            colors={m:np.asarray(Image.open(OUT/paths[m]))[:,:320] for m in packer.MODULES}
            encoded={m:np.asarray(Image.open(OUT/paths['Depth-'+m]))[:,:320] for m in packer.MODULES}
            depths={m:(z[:,:,0].astype(np.uint16)<<8)|z[:,:,1].astype(np.uint16) for m,z in encoded.items()}
            for z in encoded.values():self.assertTrue(np.all(z[:,:,2]==0),'Depth blue channel is reserved')
            # Read the body under the cloth, where both are genuinely opaque and
            # the cape has the nearer camera depth. A visible-only mask fails.
            hidden=(colors['BodyOutfit'][:,:,3]>224)&(colors['Cape'][:,:,3]>224)&(depths['Cape']<depths['BodyOutfit'])
            self.assertGreater(int(hidden.sum()),100)
            removed=packer.compose(colors,depths,[m for m in packer.MODULES if m!='Cape'])
            self.assertTrue(np.all(removed[:,:,3][hidden]>224),'Cape removal opens a body hole')
            full=packer.compose(colors,depths)
            changed=hidden&(np.max(np.abs(full[:,:,:3].astype(np.int16)-removed[:,:,:3].astype(np.int16)),axis=2)>8)
            self.assertGreater(int(changed.sum()),100)
            self.results['capeRemoval'].append({'direction':direction,'concealedBodyPixels':int(hidden.sum()),'revealedDifferentPixels':int(changed.sum()),'transparentHoles':int(np.sum(removed[:,:,3][hidden]<=224))})

    def test_holding_hand_owns_covered_hilt_pixels(self):
        for audit in self.audit['clips']:
            clip=self.clips[audit['name']]
            for sample in audit['samples']:
                for projection in sample['projections']:
                    direction=projection['direction'];x,y=[int(round(v)) for v in projection['gripPixel']]
                    with Image.open(OUT/clip['strips'][direction]['Weapon']) as image:
                        alpha=image.getpixel(((sample['frame']-1)*320+x,y))[3]
                    # A hilt is only 1–2 source pixels wide. Rounded projected
                    # centers can land on a multisampled edge. Reject a mostly
                    # exposed center; retain the actual alpha in the evidence.
                    self.assertLessEqual(alpha,160,f"Mostly exposed hilt: {audit['name']} {direction} {sample['frame']}")
                    self.results['gripSamples'].append({'action':audit['name'],'direction':direction,'frame':sample['frame'],'weaponAlphaAtHiltCenter':alpha})

    def test_no_clipping_or_degenerate_weapon_surfaces(self):
        for frames in self.validation['frames'].values():
            for record in frames:self.assertEqual(record['clippedBorderPixels'],0)
        for mesh in self.audit['meshes']:
            if mesh['module']=='Weapon':self.assertEqual(mesh['degenerateFaces'],0)
        for clip in self.audit['clips']:
            if clip['loop']:self.assertLess(clip['loopEndpointMatrixError'],1e-4)

    @classmethod
    def tearDownClass(cls):
        (OUT/'factory/integration-evidence.json').write_text(json.dumps(cls.results,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':unittest.main()
