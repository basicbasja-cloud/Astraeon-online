import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from export_review_part_sheets import export


class ReviewPartSheetTests(unittest.TestCase):
    def fixture(self,root):
        image=Image.new('RGBA',(8,8));image.putpixel((3,5),(80,40,20,150));path=root/'part.png';image.save(path)
        record={'action':'Attack','direction':'SE','index':0,'source_action':'Sword_Attack','source_frame':3,
                'parts':[{'role':'HeadHair','source_file':'part.png','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]}
        data={'canvas':{'compositionWidth':8,'compositionHeight':8,'frameWidth':4,'frameHeight':4,'rootAnchorX':2,'rootAnchorY':3},'frames':[record]}
        source=root/'samples.json';source.write_text(json.dumps(data));return source,data

    def test_lossless_sheet_keeps_rgba_and_absolute_cell_placement(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);source,_=self.fixture(root);report=export(source,root/'out',root)
            sheet=Image.open(root/'out/Attack/SE/HeadHair.png')
            self.assertEqual(sheet.getpixel((3,5)),(80,40,20,150))
            self.assertEqual(sheet.size,(32,8));self.assertEqual(report['root'],[4,6])
            self.assertEqual(report['sheets'][0]['cell_pixel_mismatches'],0)

    def test_reject_stale_pixels_and_duplicate_frames(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);source,data=self.fixture(root)
            Image.new('RGBA',(8,8),'red').save(root/'part.png')
            with self.assertRaisesRegex(ValueError,'changed'):export(source,root/'stale',root)
            source,data=self.fixture(root);data['frames']*=2;source.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Duplicate'):export(source,root/'duplicate',root)

    def test_reject_path_outside_repository(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);source,data=self.fixture(root);data['frames'][0]['parts'][0]['source_file']='../outside.png';source.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'escaped'):export(source,root/'out',root)


if __name__=='__main__':unittest.main()
