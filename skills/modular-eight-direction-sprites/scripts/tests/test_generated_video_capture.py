"""Real ffmpeg decoder fixtures, not generated character motion."""
import importlib.util,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('generated',BASE/'capture-generated-video.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'decoder unavailable')
class GeneratedCapture(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def fixture(self,path,vfr=False):
  cmd=['ffmpeg','-v','error','-f','lavfi','-i','color=c=red:size=80x96:rate=25','-frames:v','6']
  if vfr:cmd+=['-vf','setpts=(N+2*floor(N/2))/(25*TB)','-fps_mode','passthrough','-c:v','ffv1']
  else:cmd+=['-c:v','mpeg4','-bf','0']
  subprocess.run(cmd+['-threads','1',str(path)],check=True)
 def test_every_native_cfr_frame_is_kept_including_identical_holds(self):
  p=self.root/'holds.mp4';self.fixture(p);r=m.capture(p,self.root/'capture','fixture://cfr-holds',origin='decoder_fixture')
  self.assertEqual(len(r['frames']),6);self.assertEqual([f['source_pts_ms'] for f in r['frames']],[0,40,80,120,160,200]);self.assertEqual(len({f['sha256'] for f in r['frames']}),1);self.assertEqual(r['duration_ms'],240);self.assertFalse(r['production_pass']);self.assertFalse(r['rig_ground_truth'])
 def test_vfr_window_keeps_native_time_and_full_holds(self):
  p=self.root/'vfr.mkv';self.fixture(p,True);r=m.capture(p,self.root/'window','fixture://vfr',start_ms=40,end_ms=320,origin='decoder_fixture')
  self.assertEqual([f['source_index'] for f in r['frames']],[1,2,3]);self.assertEqual([f['source_pts_ms'] for f in r['frames']],[40,160,200]);self.assertEqual([f['duration_ms'] for f in r['frames']],[120,40,120]);self.assertEqual(r['motion_review'],'pending');self.assertEqual(r['camera_motion'],'unknown')
 def test_missing_final_exposure_is_not_replaced_by_average_fps(self):
  p=self.root/'unknown.mkv';self.fixture(p,True)
  with self.assertRaisesRegex(ValueError,'duration unavailable'):m.capture(p,self.root/'bad','fixture://missing-last',origin='decoder_fixture')
  self.assertFalse((self.root/'bad').exists())
 def test_renamed_gif_cannot_masquerade_as_generated_video(self):
  p=self.root/'fake.mp4';Image.new('RGB',(20,20),'red').save(p,format='GIF')
  with self.assertRaisesRegex(ValueError,'actual video container'):m.capture(p,self.root/'bad','fixture://fake',origin='decoder_fixture')
  self.assertFalse((self.root/'bad').exists())
if __name__=='__main__':unittest.main()
