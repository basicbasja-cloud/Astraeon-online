import hashlib,json,sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from pack_patch001_character import downsample_partition,validate_timing,preflight,pack,composed_draw_order,trimmed_source,atlas_pages
from export_runtime_character_policy import render

class RuntimePackTests(unittest.TestCase):
    def test_storage_trim_restores_original_pixels_and_integer_location(self):
        source=Image.new('RGBA',(64,64));ImageDraw.Draw(source).rectangle((11,17,30,40),fill=(80,100,150,120));trimmed,offset=trimmed_source(source);restored=Image.new('RGBA',source.size);restored.paste(trimmed,tuple(offset))
        self.assertEqual(offset,[11,17]);self.assertEqual(restored.tobytes(),source.tobytes());self.assertEqual(trimmed_source(Image.new('RGBA',(64,64)))[0].size,(1,1))
    def test_streamed_atlas_pages_preserve_every_trimmed_pixel(self):
        pixels=[Image.new('RGBA',(9,11),(i*20,100,70,80+i))for i in range(9)];seen={}
        for page,placements in atlas_pages(pixels,limit=32):
            self.assertLessEqual(page.width,32);self.assertLessEqual(page.height,32)
            for index,(x,y,w,h)in placements:seen[index]=page.crop((x,y,x+w,y+h)).tobytes()
        self.assertEqual(set(seen),set(range(9)))
        for index,im in enumerate(pixels):self.assertEqual(seen[index],im.tobytes())
    def test_fx_stays_behind_body_and_under_the_front_hand_occluder(self):
        base=['BodyCostume','BackAccessory','HeadHair','Weapon','WeaponHandOccluder'];roles=base+['WeaponLightBack','WeaponLightFront'];order=composed_draw_order(base,roles)
        self.assertLess(order.index('WeaponLightBack'),order.index('BodyCostume'));self.assertGreater(order.index('WeaponLightFront'),order.index('Weapon'));self.assertLess(order.index('WeaponLightFront'),order.index('WeaponHandOccluder'));self.assertLess(order.index('BodyCostume'),order.index('BackAccessory'))
        with self.assertRaises(ValueError):composed_draw_order(base+['Weapon'],roles)

    def test_reduced_parts_recompose_without_alpha_seam_darkening(self):
        body=Image.new('RGBA',(64,64));head=Image.new('RGBA',(64,64));ImageDraw.Draw(body).rectangle((9,31,55,60),fill=(40,90,60,220));ImageDraw.Draw(head).ellipse((20,3,43,30),fill=(160,110,70,230))
        parts,master=downsample_partition({'BodyCostume':body,'HeadHair':head},['BodyCostume','HeadHair'],(20,20));combined=Image.new('RGBA',(20,20))
        for im in parts.values():combined.alpha_composite(im)
        self.assertEqual(combined.tobytes(),master.tobytes());self.assertFalse(np.any((np.array(parts['BodyCostume'])[:,:,3]>0)&(np.array(parts['HeadHair'])[:,:,3]>0)))
    def test_partition_rejects_hidden_overlaps_instead_of_destroying_them(self):
        parts={'BodyCostume':Image.new('RGBA',(8,8),(30,40,50,255)),'HeadHair':Image.new('RGBA',(8,8),(70,80,90,255))}
        with self.assertRaisesRegex(ValueError,'hidden surfaces'):downsample_partition(parts,list(parts),(2,2))
    def test_partition_rejects_different_canvases(self):
        with self.assertRaises(ValueError):downsample_partition({'BodyCostume':Image.new('RGBA',(8,8)),'HeadHair':Image.new('RGBA',(4,4))},['BodyCostume','HeadHair'],(2,2))
    def test_timing_and_semantic_event_must_be_explicit_and_consistent(self):
        action={'frames':2,'loop':False};valid={'durations':[50,50],'events':[{'name':'projectileRelease','timeMs':50,'phase':.5,'frameIndex':1}]};self.assertEqual(validate_timing(action,valid)[0],[50,50])
        for bad in [{'durations':[50]}, {'durations':[True,50]}, {'durations':[50,50],'events':[{'name':'impact','timeMs':80,'phase':.8,'frameIndex':0}]},{'durations':[50,50],'events':[{'name':'impact','timeMs':50,'phase':.1,'frameIndex':1}]},{'durations':[50,50],'cycleDistance':1}]:
            with self.assertRaises(ValueError):validate_timing(action,bad)
    def test_missing_real_imports_cannot_create_any_of_the_six_runtime_packages(self):
        base=ROOT/'authoring/characters/factory-v3/patch-0.0.1';config=json.loads((base/'factory.json').read_text());ledger=json.loads((base/'ledger.json').read_text())
        with tempfile.TemporaryDirectory()as temp:
            for character in config['characters']:
                with self.assertRaisesRegex(ValueError,'actual cutout import missing'):preflight(character,config,ledger,Path(temp),{})
    def test_runtime_policy_is_generated_from_current_factory_contract(self):
        config=json.loads((ROOT/'authoring/characters/factory-v3/patch-0.0.1/factory.json').read_text());self.assertEqual((ROOT/'patch001-characters.js').read_text(),render(config))
    def test_complete_synthetic_import_packs_into_valid_runtime_metadata(self):
        # Colored rectangles are isolated test data, never playable artwork.
        with tempfile.TemporaryDirectory()as temp:
            repo=Path(temp);base=repo/'factory';base.mkdir();directions=['S','SW','W','NW','N','NE','E','SE'];four=['SW','NW','NE','SE'];mapping=dict(zip(directions,['SE','SW','SW','NW','NW','NE','NE','SE']));character={'id':'swordsman-male-test-fixture','class':'Swordsman','body_variant':'male'}
            actions={name:{'frames':2,'loop':name in ['Idle','Walk','Run'],'authored_directions':four if name in ['BasicAttack','SkillAction']else directions,'direction_map':mapping if name in ['BasicAttack','SkillAction']else dict(zip(directions,directions))}for name in ['Idle','Walk','Run','BasicAttack','SkillAction','Hit','Death','Guard','Dash']}
            config={'classes':{'Swordsman':{'actions':actions}},'characters':[character],'canvas':{'runtime':[240,240],'authoring':[768,768],'runtime_root':[120,172],'runtime_reference_height':88},'direction_inputs':directions};job={'id':'fixture','character':character['id'],'guide_job':'fixture-guide','fit_id':'fixture-fit','actions':list(actions)};index={'assets':{},'objects':{}};roles=['BodyCostume','HeadHair','Weapon']
            for i,role in enumerate(roles):
                im=Image.new('RGBA',(768,768));ImageDraw.Draw(im).rectangle((50+i*100,100,300 if i==0 else 100+i*100,150),fill=(50+i*70,100,60,255));pixels=np.array(im);key=hashlib.sha256(pixels.tobytes()).hexdigest();path=repo/(role+'.png');im.save(path);index['objects'][key]={'file':path.name};index['assets'][role]={'object':key,'role':role,'fit_id':'fixture-fit','pose_id':'fixture-pose','camera_id':'fixture-camera','root':[384,550.4],'canvas':[768,768]}
            sockets={s:[384,550.4]for s in ['root','head','hand_R','hand_L','back','waist']};frames=[{'direction':d,'index':i,'pose_id':'fixture-pose','camera_id':'fixture-camera','sockets':sockets,'base_draw_order':roles,'assets':{r:r for r in roles}}for d in directions for i in range(2)]
            def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
            write(base/'factory.json',config);write(base/'ledger.json',{'paint_jobs':{'fixture':job}});write(base/'cutout-store/index.json',index);write(base/'cutouts/fixture/bindings.json',{'paint_job':'fixture','character':character['id'],'frames':frames});write(base/'cutouts/fixture/import-receipt.json',{'paint_job':'fixture','guide_job':'fixture-guide','all_frames_present':True,'recomposition_mismatches':0});write(base/'timing.json',{name:{'durations':[50,50],'events':[{'name':'impact','timeMs':50,'phase':.5,'frameIndex':1}]}for name in actions})
            result=pack(character['id'],base/'timing.json',repo,base);target=repo/'assets/characters'/character['id'];definition=json.loads((target/'sprite.json').read_text())
            self.assertEqual(result['base_recomposition_mismatches'],0);self.assertEqual(len(definition['clips']),9);self.assertEqual(len(definition['clips']['BasicAttack']['directions']),4);self.assertEqual(len(definition['clips']['Walk']['directions']),8);self.assertLessEqual(result['unique_pixel_frames'],3);self.assertFalse(result['runtime_admitted']);self.assertEqual(definition['clips']['Idle']['directions']['S']['frames'][0]['sockets']['root'],[120,172])
            self.assertTrue(all((repo/a['file']).is_file()for a in definition['atlases'].values()))
            self.assertEqual(definition['canvas']['compositionWidth'],768);self.assertEqual(result['raster_mode'],'source-composite')
            body=definition['parts']['body-costume'];ref=next(iter(body['frames'].values()));atlas=Image.open(repo/definition['atlases'][ref['atlasId']]['file']);x,y,w,h=ref['rect'];restored=Image.new('RGBA',(768,768));restored.paste(atlas.crop((x,y,x+w,y+h)),tuple(ref['offset']))
            self.assertEqual(restored.tobytes(),Image.open(repo/'BodyCostume.png').tobytes(),'The opaque body beneath the head and weapon must survive packing')

if __name__=='__main__':unittest.main()
