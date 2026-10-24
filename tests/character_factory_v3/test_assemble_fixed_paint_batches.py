import json
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image,PngImagePlugin
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from assemble_fixed_paint_batches import assemble
from normalize_fixed_viewport_batch import normalize_batch
from track_visible_cutouts import sha
from source_capture_identity import seal_source_reference


class FixedBatchAssemblyTests(unittest.TestCase):
    def fixture(self,root):
        guide=root/'guide';(guide/'NE').mkdir(parents=True)
        for i in range(4):
            image=Image.new('RGBA',(16,16));image.paste((50+i*20,70,90,255),(4,4,12,12));image.save(guide/'NE'/f'{i:03d}.png')
        manifest={'job':{'id':'fixture'},'frame_count':4,'views':{'NE':{'frames':[{'action':'Cast','source_frame':i}for i in range(4)]}}};(guide/'manifest.json').write_text(json.dumps(manifest));batches=[]
        for n in range(2):
            folder=root/f'batch-{n}';(folder/'frames').mkdir(parents=True);indices=[n*2,n*2+1];sheet=Image.new('RGBA',(32,16))
            for slot,i in enumerate(indices):sheet.paste(Image.open(guide/'NE'/f'{i:03d}.png'),(slot*16,0))
            sheet.save(folder/'raw.png');recipe={'grid':[2,1],'source_size':[16,16],'viewport':[0,0,16,16],'canonical_root':[8,14],'source_pose_indices':indices,'frame_space':'canonical-authoring','guide_job':'fixture','guide_manifest_sha256':sha(guide/'manifest.json'),'direction':'NE','all_source_frame_inputs':[{'index':i,'sha256':sha(guide/'NE'/f'{i:03d}.png')}for i in range(4)]};(folder/'viewport.json').write_text(json.dumps(recipe));images,receipt=normalize_batch(sheet,recipe)
            for im,i in zip(images,indices):im.save(folder/'frames'/f'{i:03d}.png')
            receipt['inputs']={key:{'sha256':sha(path)}for key,path in [('sheet',folder/'raw.png'),('recipe',folder/'viewport.json')]};(folder/'frames/receipt.json').write_text(json.dumps(receipt));batches.append(folder)
        return guide,batches

    def test_complete_reversed_batches_preserve_every_pixel_and_timeline(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide,batches=self.fixture(root);result=assemble(guide,list(reversed(batches)),root/'out')
            self.assertEqual([r['index']for r in result['frames']],[0,1,2,3]);self.assertFalse(result['paint_anatomy_matches_source_certified']);self.assertTrue(result['normalized_pixel_positions_preserved'])
            for i in range(4):np.testing.assert_array_equal(np.array(Image.open(guide/'NE'/f'{i:03d}.png')),np.array(Image.open(root/'out/frames'/f'{i:03d}.png')))

    def test_missing_poses_are_not_fabricated(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide,batches=self.fixture(root)
            with self.assertRaisesRegex(ValueError,'Complete source timeline'):assemble(guide,batches[:1],root/'out')

    def test_duplicate_pose_is_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide,batches=self.fixture(root)
            with self.assertRaisesRegex(ValueError,'Duplicate'):assemble(guide,[batches[0],batches[0]],root/'out')

    def test_changed_raw_is_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide,batches=self.fixture(root);Image.new('RGBA',(32,16),(250,30,20,255)).save(batches[0]/'raw.png')
            with self.assertRaisesRegex(ValueError,'input changed'):assemble(guide,batches,root/'out')

    def test_moved_normalized_pixel_is_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide,batches=self.fixture(root);path=batches[0]/'frames/000.png';im=Image.open(path);im.putpixel((3,3),(10,20,30,255));im.save(path)
            with self.assertRaisesRegex(ValueError,'fixed raw-sheet normalization'):assemble(guide,batches,root/'out')

    def test_changed_source_png_is_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide,batches=self.fixture(root);Image.new('RGBA',(16,16)).save(guide/'NE/000.png')
            with self.assertRaisesRegex(ValueError,'Source reference changed'):assemble(guide,batches,root/'out')

    def test_sealed_batches_rebuild_after_capture_metadata_only_changes(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide,batches=self.fixture(root)
            for folder in batches:seal_source_reference(folder/'viewport.json',guide)
            path=guide/'manifest.json';data=json.loads(path.read_text());data['png_normalization']={'original_sha256':'new-render-date'};path.write_text(json.dumps(data))
            for path in (guide/'NE').glob('*.png'):
                im=Image.open(path).copy();info=PngImagePlugin.PngInfo();info.add_text('Date','new-render-date');im.save(path,pnginfo=info,compress_level=0)
            result=assemble(guide,batches,root/'out')
            self.assertTrue(all(r['source_capture_verification']['mode']=='EXACT_POSE_AND_VISIBLE_RGBA'for r in result['batches']))
            for i in range(4):np.testing.assert_array_equal(np.array(Image.open(guide/'NE'/f'{i:03d}.png')),np.array(Image.open(root/'out/frames'/f'{i:03d}.png')))

    def test_sealed_batches_still_reject_actual_source_pixel_changes(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide,batches=self.fixture(root)
            for folder in batches:seal_source_reference(folder/'viewport.json',guide)
            path=guide/'NE/000.png';im=Image.open(path);im.putpixel((5,5),(250,10,20,255));im.save(path)
            with self.assertRaisesRegex(ValueError,'visible RGBA changed'):assemble(guide,batches,root/'out')


if __name__=='__main__':unittest.main()
