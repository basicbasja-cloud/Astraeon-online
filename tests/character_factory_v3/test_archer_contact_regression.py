"""Integration regression; requires Blender and the retained local CC0 inputs."""
import json,shutil,subprocess,unittest,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class ArcherContactRegression(unittest.TestCase):
    @unittest.skipUnless(shutil.which('blender'),'Blender unavailable')
    def test_stale_implementation_is_rejected_before_source_capture(self):
        for field in ['renderer_sha256','retarget_implementation_sha256','floor_sit_implementation_sha256']:
            with self.subTest(field=field),tempfile.TemporaryDirectory()as temp:
                folder=Path(temp);job=folder/'job.json';job.write_text(json.dumps({'source_file':'missing-source.glb',field:'0'*64}))
                result=subprocess.run(['blender','-b','-t','2','--python-exit-code','1','--python',str(ROOT/'tools/character_factory_v3/render_patch001_guides.py'),'--','--job',str(job),'--output',str(folder/'capture')],cwd=ROOT,capture_output=True,text=True,timeout=60)
                self.assertNotEqual(result.returncode,0);self.assertIn('Job implementation changed after planning',result.stdout+result.stderr);self.assertFalse(list(folder.rglob('*.png')))

    @unittest.skipUnless(shutil.which('blender'),'Blender unavailable')
    def test_real_donor_contact_and_grip_states(self):
        result=subprocess.run(['blender','-b','-t','2','--python-exit-code','1','--python',str(Path(__file__).with_name('blender_archer_contact_regression.py'))],cwd=ROOT,capture_output=True,text=True,timeout=180)
        self.assertEqual(result.returncode,0,(result.stdout+result.stderr)[-6000:])
        records=[line.removeprefix('ARCHER_CONTACT_REGRESSION ')for line in result.stdout.splitlines()if line.startswith('ARCHER_CONTACT_REGRESSION ')]
        self.assertEqual(len(records),1,'Missing actual Blender regression receipt')
        report=json.loads(records[0]);self.assertEqual(report['status'],'PASS');self.assertGreaterEqual(report['sampled_poses'],18);self.assertLess(report['corrected_max_toe_error_m'],1e-4)
        print('Actual Blender:',json.dumps({k:v for k,v in report.items()if k!='records'}))

if __name__=='__main__':unittest.main()
