"""Negative asset checks and deterministic full-strip registration/packing."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageDraw
import jsonschema
ROOT=Path(__file__).resolve().parents[1]

def tool(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
normalize=tool('normalize-modular-strip').normalize
pack=tool('pack-modular-sprites').pack
validator=tool('validate-sprites')

class SpriteTools(unittest.TestCase):
    def definition(self):
        return {'characterId':'test-character','directions':['S','SW','W','NW','N','NE','E','SE'],
                'source':{'normalization':{'sourceFrameWidth':8,'sourceFrameHeight':8,'sourceRootAnchor':[4,6],'scale':1}},
                'canvas':{'frameWidth':12,'frameHeight':12,'rootAnchorX':6,'rootAnchorY':9,'referenceHeight':6},
                'clips':{'Idle':{'durations':[100,200]}},'parts':{'weapon':{'slot':'Weapon','frames':{}}},'atlases':{}}
    def strip(self,path):
        image=Image.new('RGBA',(16,64));draw=ImageDraw.Draw(image)
        for row in range(8):
            draw.point((4,row*8+6),fill=(row+1,90,120,255))
            draw.point((12,row*8+6),fill=(row+1,140,170,255))
        path.parent.mkdir(parents=True,exist_ok=True);image.save(path)
    def test_whole_strip_reorder_preserves_shared_root_and_pose_offsets(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);source=folder/'input.png';out=folder/'normalized.png';self.strip(source);d=self.definition()
            order=list(reversed(d['directions']));normalize(d,'Idle',source,out,order)
            image=Image.open(out);self.assertEqual(image.size,(24,96))
            for row,direction in enumerate(d['directions']):
                self.assertEqual(image.getpixel((6,row*12+9)),(order.index(direction)+1,90,120,255))
                self.assertEqual(image.getpixel((18,row*12+9)),(order.index(direction)+1,140,170,255))
    def test_normalize_rejects_clipped_paint_wrong_rows_and_opaque_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);source=folder/'input.png';out=folder/'normalized.png';self.strip(source);d=self.definition()
            with self.assertRaises(ValueError):normalize(d,'Idle',source,out,['S']*8)
            d['source']['normalization']['sourceRootAnchor']=[-50,-50]
            with self.assertRaises(ValueError):normalize(d,'Idle',source,out,d['directions'])
            Image.new('RGB',(16,64)).save(source)
            with self.assertRaises(ValueError):normalize(self.definition(),'Idle',source,out,d['directions'])
    def test_packer_is_lossless_deterministic_and_adds_empty_gutters(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);d=self.definition();source=root/'sources/parts/weapon/Idle/strip.png';self.strip(root/'raw.png')
            normalize(d,'Idle',root/'raw.png',source,d['directions'])
            target=pack(d,root/'sources',root);first=target.read_bytes();atlas=root/'assets/characters/test-character/atlases/weapon-idle.png';pixels=atlas.read_bytes()
            image=Image.open(atlas);self.assertEqual(image.mode,'RGBA')
            for row,direction in enumerate(d['directions']):
                ref=d['parts']['weapon']['frames'][f'test-character_weapon_Idle_{direction}_00'];x,y,w,h=ref['rect']
                self.assertEqual(image.getpixel((x+6,y+9)),(row+1,90,120,255));self.assertEqual(image.getpixel((x-1,y)),(0,0,0,0))
            pack(d,root/'sources',root);self.assertEqual(first,target.read_bytes());self.assertEqual(pixels,atlas.read_bytes())
    def test_missing_strip_cannot_publish_partial_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaises(FileNotFoundError):pack(self.definition(),root/'sources',root)
            self.assertFalse((root/'assets').exists())
    def test_dedup_preserves_full_canvas_aliases_and_shares_empty_slots(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);d=self.definition();d['parts']['empty']={'slot':'Headgear','frames':{}}
            d['clips']['Walk']={'durations':[100,200]}
            for part in d['parts']:
                for clip in d['clips']:
                    image=Image.new('RGBA',(24,96))
                    if part=='weapon':
                        for row in range(8):
                            for index in range(2):image.putpixel((index*12+6,row*12+9),(120,140,160,255))
                    path=root/'sources/parts'/part/clip/'strip.png';path.parent.mkdir(parents=True,exist_ok=True);image.save(path)
            pack(d,root/'sources',root,deduplicate=True)
            self.assertEqual(len(d['atlases']),2)
            for atlas in d['atlases'].values():self.assertEqual((atlas['width'],atlas['height']),(16,16))
            refs=list(d['parts']['weapon']['frames'].values());self.assertEqual(len({tuple(ref['rect']) for ref in refs}),1)
            self.assertEqual({ref['atlasId'] for ref in refs},{'weapon-idle'})
            self.assertEqual({ref['atlasId'] for ref in d['parts']['empty']['frames'].values()},{'empty'})
            im=Image.open(root/d['atlases']['weapon-idle']['file']);self.assertEqual(im.getpixel((8,11)),(120,140,160,255))
    def test_duplicate_frame_ids_and_unknown_timing_fields_fail(self):
        with self.assertRaises(ValueError):validator.unique_object([('same-frame',1),('same-frame',2)])
        schema=json.loads((ROOT/'assets/characters/schemas/sprite-definition.schema.json').read_text())
        d=json.loads((ROOT/'assets/characters/swordsman-proof/sprite.json').read_text());d['parts']['hair']['duration']=100
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(d,schema)
    def test_shared_character_atlas_is_allowed_but_escaping_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);file=root/'assets/characters/test-character/sprite.json';file.parent.mkdir(parents=True)
            relative='assets/characters/shared/empty.png';imagepath=root/relative;imagepath.parent.mkdir()
            tiny={'characterId':'test-character','canvas':{'frameWidth':4,'frameHeight':4},'atlases':{'empty':{'file':relative,'width':8,'height':8}},'parts':{'body':{'frames':{'frame':{'atlasId':'empty','rect':[2,2,4,4]}}}}}
            file.write_text(json.dumps(tiny));Image.new('RGBA',(8,8)).save(imagepath)
            self.assertEqual(validator.validate_file(file,root,{}),(1,1))
            outside=root/'outside.png';imagepath.replace(outside);imagepath.symlink_to(outside)
            with self.assertRaisesRegex(ValueError,'outside character asset namespace'):validator.validate_file(file,root,{})
    def test_validator_rejects_actual_missing_or_wrong_size_images_and_bleed(self):
        d=json.loads((ROOT/'assets/characters/swordsman-proof/sprite.json').read_text());atlas_id=next(iter(d['atlases']))
        # A tiny definition/schema isolates actual image checks; metadata semantics
        # are separately exercised with the complete runtime fixture.
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);file=root/'assets/characters/test-character/sprite.json';file.parent.mkdir(parents=True)
            relative='assets/characters/test-character/atlases/test.png';imagepath=root/relative
            tiny={'characterId':'test-character','canvas':{'frameWidth':4,'frameHeight':4},'atlases':{'test':{'file':relative,'width':8,'height':8}},'parts':{'body':{'frames':{'frame':{'atlasId':'test','rect':[2,2,4,4]}}}}}
            file.write_text(json.dumps(tiny))
            with self.assertRaises(OSError):validator.validate_file(file,root,{})
            imagepath.parent.mkdir();Image.new('RGBA',(7,8)).save(imagepath)
            with self.assertRaises(ValueError):validator.validate_file(file,root,{})
            image=Image.new('RGBA',(8,8));image.putpixel((1,3),(255,0,0,255));image.save(imagepath)
            with self.assertRaises(ValueError):validator.validate_file(file,root,{})
            image=Image.new('RGBA',(8,8));image.putpixel((3,3),(255,0,0,255));image.save(imagepath)
            self.assertEqual(validator.validate_file(file,root,{}),(1,1))

if __name__=='__main__':unittest.main()
