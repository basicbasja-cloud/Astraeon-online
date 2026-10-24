import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from review_fixed_paint_sequence import alpha_distances,review,sha,shared_palette_gif


class FixedPaintSequenceReviewTests(unittest.TestCase):
    def test_alpha_probe_is_distance_only(self):
        image=Image.new('RGBA',(32,32));image.putpixel((10,10),(20,30,40,255))
        self.assertEqual(alpha_distances(image,{'at':[10,10],'away':[13,14]}),{'at':0.,'away':5.})
        for sockets in [{'bad':[float('nan'),0]},{'bad':[100,1]}]:
            with self.assertRaises(ValueError):alpha_distances(image,sockets)
        with self.assertRaises(ValueError):alpha_distances(Image.new('RGBA',(32,32)),{'at':[1,1]})

    def test_review_pins_source_and_preserves_frames(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);guide=root/'guide';frames=root/'frames';frames.mkdir();(guide/'SE').mkdir(parents=True)
            image=Image.new('RGBA',(32,32));image.paste((80,40,30,255),(10,10,20,20));image.save(frames/'000.png')
            image.resize((64,64)).save(guide/'SE/000.png')
            m={'job':{'id':'test','resolution':64},'frame_count':1,'views':{'SE':{'frames':[{'action':'Idle','source_frame':0,'landmarks':{'head':[24,24]},'weapon_guide':{}}]}}}
            (guide/'manifest.json').write_text(json.dumps(m));recipe={'frame_space':'canonical-authoring','guide_job':'test','guide_manifest_sha256':sha(guide/'manifest.json'),'direction':'SE','source_pose_indices':[0],'source_size':[32,32],'all_source_frame_inputs':[{'index':0,'sha256':sha(guide/'SE/000.png')}]}
            path=root/'recipe.json';path.write_text(json.dumps(recipe));original=sha(frames/'000.png')
            result=review(guide,path,frames,root/'out')
            self.assertTrue(result['full_source_timeline']);self.assertFalse(result['runtime_admitted']);self.assertEqual(sha(frames/'000.png'),original)
            self.assertTrue((root/'out/source-vs-paint-slow.gif').is_file())
            image.putpixel((0,0),(255,0,0,255));image.resize((64,64)).save(guide/'SE/000.png')
            with self.assertRaises(ValueError):review(guide,path,frames,root/'stale')

    def test_gif_retains_one_palette_for_different_frames(self):
        with tempfile.TemporaryDirectory()as tmp:
            path=Path(tmp)/'test.gif';a=Image.new('RGB',(16,16),'red');b=Image.new('RGB',(16,16),'blue')
            shared_palette_gif([a,b],path,80)
            with Image.open(path)as image:
                self.assertEqual(image.n_frames,2);self.assertEqual(image.convert('RGB').getpixel((0,0)),(255,0,0));image.seek(1)
                self.assertEqual(image.convert('RGB').getpixel((0,0)),(0,0,255));self.assertEqual(image.info['duration'],80)


if __name__=='__main__':unittest.main()
