"""Real bounded-exposure/crop fixtures and failure checks; no pose detector."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from PIL import Image

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('capture',BASE/'capture-reference.py')
capture = importlib.util.module_from_spec(spec); spec.loader.exec_module(capture)

class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.source = self.root/'motion.png'
        a = Image.new('RGBA',(12,12)); a.putpixel((2,3),(255,0,0,255))
        b = Image.new('RGBA',(12,12)); b.putpixel((8,7),(0,255,0,255))
        a.save(self.source,save_all=True,append_images=[b,a],duration=[70,130,90],loop=0)
    def tearDown(self): self.temp.cleanup()
    def test_onset_window_keeps_original_pts_and_complete_last_exposure(self):
        result = capture.extract(self.source,self.root/'window','fixture',start_ms=70,end_ms=201,crop=[1,2,8,8])
        self.assertEqual([f['source_index'] for f in result['frames']],[1,2])
        self.assertEqual([f['source_pts_ms'] for f in result['frames']],[70,200])
        self.assertEqual([f['time_ms'] for f in result['frames']],[0,130])
        self.assertEqual([f['duration_ms'] for f in result['frames']],[130,90])
        self.assertEqual(result['duration_ms'],220)  # end boundary does not shorten a pose
        with Image.open(self.root/'window/0000.png') as im:
            self.assertEqual(im.size,(8,8)); self.assertEqual(im.getpixel((7,5)),(0,255,0,255))
        self.assertEqual(result['source_xy_to_study_xy']['subtract_xy'],[1,2])
    def test_crop_never_pads_or_clamps_and_failure_is_atomic(self):
        with self.assertRaisesRegex(ValueError,'exceeds source canvas'):
            capture.extract(self.source,self.root/'bad','fixture',crop=[5,5,8,8])
        self.assertFalse((self.root/'bad').exists()); self.assertFalse(list(self.root.glob('.reference-*')))
    def test_invalid_empty_and_over_limit_windows_fail(self):
        for args in [dict(start_ms=70,end_ms=70),dict(start_ms=float('nan')),dict(start_ms=500),dict(limit=1)]:
            with self.subTest(args=args),self.assertRaises(ValueError):
                capture.extract(self.source,self.root/'bad','fixture',**args)
            self.assertFalse((self.root/'bad').exists())
    def test_unknown_timing_cannot_be_selected_as_a_timed_window(self):
        still = self.root/'still.png'; Image.new('RGBA',(12,12)).save(still)
        with self.assertRaisesRegex(ValueError,'timed window'):
            capture.extract(still,self.root/'bad','fixture',allow_untimed=True,start_ms=0,end_ms=50)
        self.assertFalse((self.root/'bad').exists())
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'video tools absent')
    def test_actual_vfr_decode_is_not_resampled_or_seek_shifted(self):
        video = self.root/'vfr.mkv'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc=size=32x24:rate=25:duration=0.12',
                        '-vf',r'settb=1/1000,setpts=if(eq(N\,0)\,0\,if(eq(N\,1)\,70\,200))',
                        '-fps_mode','passthrough','-enc_time_base','1/1000','-c:v','ffv1',str(video)],check=True)
        result = capture.extract(video,self.root/'video','fixture',limit=1,start_ms=70,end_ms=200,crop=[0,0,16,12])
        self.assertEqual(len(result['frames']),1); f = result['frames'][0]
        self.assertEqual((f['source_index'],f['source_pts_ms'],f['duration_ms']),(1,70,130))
        self.assertEqual(result['canvas'],(16,12))
        # FFV1 fixture genuinely has no reported last-frame hold. Never fill with average FPS.
        with self.assertRaisesRegex(ValueError,'duration unavailable'):
            capture.extract(video,self.root/'missing-last','fixture')
        self.assertFalse((self.root/'missing-last').exists())

if __name__ == '__main__': unittest.main(verbosity=2)
