import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw

spec=importlib.util.spec_from_file_location('study',Path(__file__).resolve().parents[1]/'tools/export_character_pose_study.py')
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)


class PoseStudyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.image=Image.new('RGBA',(48,32));draw=ImageDraw.Draw(self.image)
        for i in range(6):
            x,y=i%3*16,i//3*16
            draw.rectangle((x+4,y+4,x+9,y+12),fill=(30+i*20,90,140,255))
        self.image.save(self.root/'source.png')
        motion={'registration':{'canvas':[32,32],'root':{'x':16,'y':28}},'actions':{'BasicAttack':{'directions':{
            d:{'frames':[{'durationMs':n} for n in [100,30,40,50,60,170]]} for d in study.DIRECTIONS}}}}
        (self.root/'motion.json').write_text(json.dumps(motion))
        self.plan={'schemaVersion':'1.0','action':'BasicAttack','motionTemplate':'motion.json',
                   'timelineToPose':list(range(6)),'phases':['ready','windup','swing','contact','follow','return'],
                   'sourceCell':[16,16],'sharedScale':1,'sheets':{d:{'file':'source.png','root':[8,14]} for d in study.DIRECTIONS}}

    def tearDown(self):self.temp.cleanup()

    def test_exact_clock_and_deterministic_original_pixels(self):
        before=(self.root/'source.png').read_bytes()
        a=study.export(self.plan,self.root,self.root/'a');b=study.export(self.plan,self.root,self.root/'b')
        self.assertEqual(a,b);self.assertFalse(a['visualApproval']);self.assertEqual(len(a['frames']),48)
        self.assertEqual(before,(self.root/'source.png').read_bytes())
        for suffix,duration in [('normal',450),('half',900)]:
            path=self.root/f'a/BasicAttack-{suffix}.png'
            with Image.open(path) as im:
                self.assertEqual(sum((im.seek(i) or im.info['duration']) for i in range(im.n_frames)),duration)
            self.assertEqual(path.read_bytes(),(self.root/f'b/BasicAttack-{suffix}.png').read_bytes())

    def test_missing_direction_and_blank_source_fail_before_export(self):
        del self.plan['sheets']['NE']
        with self.assertRaisesRegex(ValueError,'eight'):study.export(self.plan,self.root,self.root/'out')
        self.plan['sheets']={d:{'file':'source.png','root':[8,14]} for d in study.DIRECTIONS}
        Image.new('RGBA',(48,32)).save(self.root/'source.png')
        with self.assertRaisesRegex(ValueError,'visible art'):study.export(self.plan,self.root,self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_review_does_not_hide_boundary_failures(self):
        self.image.putpixel((15,8),(255,0,0,255));self.image.save(self.root/'source.png')
        r=study.export(self.plan,self.root,self.root/'out')
        self.assertEqual(len(r['findings']),8)
        self.assertTrue(all(f['severity']=='BLOCKING' for f in r['findings']))
        self.assertEqual(r['status'],'STUDY_ONLY')

    def test_private_reference_cannot_be_published_as_original_art(self):
        self.plan['sheets']['S']['file']='private-ro-reference/source.png'
        with self.assertRaisesRegex(ValueError,'original'):study.export(self.plan,self.root,self.root/'out')

    def test_explicit_alpha_noise_floor_preserves_source_and_reports_cleanup(self):
        self.image.putpixel((0,0),(70,40,20,8));self.image.save(self.root/'source.png')
        before=(self.root/'source.png').read_bytes();self.plan['alphaFloor']=16
        r=study.export(self.plan,self.root,self.root/'out')
        self.assertEqual(r['alphaFloor'],16)
        self.assertTrue(all(s['alphaNoisePixelsRemoved']==1 for s in r['sources']))
        self.assertEqual(before,(self.root/'source.png').read_bytes())
        self.plan['alphaFloor']=128
        with self.assertRaisesRegex(ValueError,'noise floor'):study.export(self.plan,self.root,self.root/'bad')


if __name__=='__main__':unittest.main()
