"""Exercise late failures against real PNGs, derived labels and the shared store."""
import hashlib
import json
import os
from contextlib import ExitStack,contextmanager
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import cutout_asset_store as store
import import_patch001_cutouts as importer


def snapshot(root):
    return {str(p.relative_to(root)):p.read_bytes()for p in root.rglob('*')if p.is_file()}


class CutoutImportTransactionTests(unittest.TestCase):
    @contextmanager
    def fixture(self,labels=False,seed=True):
        with tempfile.TemporaryDirectory()as temporary,ExitStack()as stack:
            root=Path(temporary);base=root/'factory';base.mkdir();cas=root/'store'
            for module,name,value in ((importer,'ROOT',root),(importer,'BASE',base),(importer,'STORE',cas),
                                      (store,'ROOT',root),(store,'STORE',cas)):
                stack.enter_context(patch.object(module,name,value))
            stack.enter_context(patch.object(importer,'receipt_valid',return_value=True))
            write=lambda path,data:path.write_text(json.dumps(data,indent=2)+'\n')
            write(base/'factory.json',{'canvas':{'authoring':[512,512],'authoring_root':[256,422.4]}})
            job={'id':'job','guide_job':'guide','fit_id':'fit','directions':['SW'],'frame_count':2,
                 'character':'fixture-not-a-production-character','actions':['BasicAttack']}
            write(base/'ledger.json',{'paint_jobs':{'job':job},'guide_jobs':{'guide':{'source_sha256':'fixture'}}})
            guide=base/'guides/guide';guide.mkdir(parents=True)
            write(guide/'manifest.json',{'frame_count':2,'views':{'SW':{'camera':{'fixed':True},'frames':[
                {'action':'Fixture','source_frame':i,'world_landmarks':{},'bone_rotations':{}}for i in range(2)]}}})
            prior=base/'cutouts/prior-job';prior.mkdir(parents=True);(prior/'bindings.json').write_bytes(b'preserve-prior-job')
            inputs=root/'inputs';inputs.mkdir();records=[]
            for i in range(2):
                folder=inputs/f'{i:03}';folder.mkdir();master=np.zeros((512,512,4),dtype=np.uint8)
                ids=np.zeros((512,512),dtype=np.uint8);parts={}
                for label,role in enumerate(('BodyCostume','HeadHair','Weapon'),1):
                    pixels=np.zeros_like(master);x=100+label*20;y=150+i*20
                    pixels[y:y+3,x:x+3]=[30+label*20,40+i*10,70,255]
                    Image.fromarray(pixels).save(folder/f'{role}.png');parts[role]=f'{i:03}/{role}.png'
                    master[pixels[:,:,3]>0]=pixels[pixels[:,:,3]>0];ids[pixels[:,:,3]>0]=label
                Image.fromarray(master).save(folder/'master.png');Image.fromarray(ids).save(folder/'labels.png')
                record={'direction':'SW','index':i,'master':f'{i:03}/master.png',
                        'sockets':{name:[256,422.4]if name=='root'else[200.0,250.0]
                                   for name in ('root','head','hand_R','hand_L','back','waist')}}
                record.update({'labels':f'{i:03}/labels.png'}if labels else{'parts':parts})
                records.append(record)
            manifest=inputs/'manifest.json';write(manifest,{'guide_job':'guide','fit_id':'fit','frames':records})
            if seed:
                prior_image=root/'prior.png';Image.new('RGBA',(512,512),(17,37,57,255)).save(prior_image)
                store.register(prior_image,{'role':'Weapon','canvas':[512,512],'fit_id':'old','pose_id':'old',
                                            'camera_id':'old','root':[256,422.4],'source_reference':'prior.png'})
                (cas/'index.json.tmp').write_bytes(b'preserve-old-temp-file')
            yield root,base,cas,manifest

    def assert_no_intake(self,base):
        self.assertFalse((base/'cutouts/job').exists())
        self.assertFalse(list((base/'cutouts').glob('.job-intake-*')))

    def test_final_frame_recomposition_failure_leaves_no_objects_or_import(self):
        with self.fixture()as(root,base,cas,manifest):
            Image.new('RGBA',(512,512)).save(root/'inputs/001/Weapon.png')
            before=snapshot(root)
            with self.assertRaisesRegex(ValueError,'recomposition differs'):
                importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(root),before)

    def test_final_frame_invalid_labels_removes_earlier_derived_parts(self):
        with self.fixture(labels=True)as(root,base,cas,manifest):
            Image.new('L',(512,512)).save(root/'inputs/001/labels.png')
            before=snapshot(root)
            with self.assertRaisesRegex(ValueError,'lack semantic labels'):
                importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(root),before)

    def test_object_publication_failure_rolls_back_only_new_objects(self):
        with self.fixture()as(root,base,cas,manifest):
            before=snapshot(root);link=os.link;calls=[]
            def fail_second(source,target):
                if Path(target).suffix=='.png':
                    calls.append(target)
                    if len(calls)==2:raise PermissionError('simulated object publication failure')
                return link(source,target)
            with patch.object(importer.os,'link',side_effect=fail_second):
                with self.assertRaisesRegex(PermissionError,'publication failure'):
                    importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(root),before)

    def test_index_write_failure_preserves_existing_index_and_temp(self):
        with self.fixture(labels=True)as(root,base,cas,manifest):
            before=snapshot(root)
            with patch.object(importer,'save_index',side_effect=OSError('simulated index write failure')):
                with self.assertRaisesRegex(OSError,'index write failure'):
                    importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(root),before)

    def test_receipt_failure_restores_index_after_its_successful_replacement(self):
        for seed in (True,False):
            with self.subTest(existing_store=seed),self.fixture(labels=True,seed=seed)as(root,base,cas,manifest):
                before=snapshot(root);link=os.link
                def fail_receipt(source,target):
                    if Path(target).name=='import-receipt.json':
                        self.assertTrue((cas/'index.json').is_file())
                        raise PermissionError('simulated final receipt failure')
                    return link(source,target)
                with patch.object(importer.os,'link',side_effect=fail_receipt):
                    with self.assertRaisesRegex(PermissionError,'receipt failure'):
                        importer.import_job('job',manifest)
                self.assert_no_intake(base);self.assertEqual(snapshot(root),before)

    def test_failed_intake_can_be_retried_without_deleting_partial_output(self):
        with self.fixture(labels=True)as(root,base,cas,manifest):
            original=json.loads(manifest.read_text());broken=json.loads(manifest.read_text())
            broken['frames'][1]['sockets']['root']=[0,0];manifest.write_text(json.dumps(broken))
            before=snapshot(cas)
            with self.assertRaisesRegex(ValueError,'root must be explicit'):
                importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(cas),before)
            manifest.write_text(json.dumps(original));importer.import_job('job',manifest)
            self.assertTrue((base/'cutouts/job/import-receipt.json').is_file())

    def test_success_publishes_derived_parts_and_resolvable_bindings_last(self):
        with self.fixture(labels=True)as(root,base,cas,manifest):
            old_index=json.loads((cas/'index.json').read_text());before=snapshot(cas);register=importer.register;seen=[]
            def watch_staging(*args,**kwargs):
                self.assertEqual(snapshot(cas),before)
                self.assertFalse((base/'cutouts/job').exists())
                self.assertIsNotNone(kwargs.get('staging_dir'));seen.append(args)
                return register(*args,**kwargs)
            with patch.object(importer,'register',side_effect=watch_staging):
                importer.import_job('job',manifest)
            folder=base/'cutouts/job';receipt=json.loads((folder/'import-receipt.json').read_text())
            self.assertEqual(receipt['frames'],2);self.assertEqual(receipt['staged_import_revision'],1)
            self.assertFalse(receipt['owner_approved']);self.assertFalse(receipt['runtime_admitted'])
            self.assertEqual(len(seen),14)
            bindings=json.loads((folder/'bindings.json').read_text())['frames'];index=json.loads((cas/'index.json').read_text())
            for key,value in old_index['assets'].items():self.assertEqual(index['assets'][key],value)
            for frame in bindings:
                merged=Image.new('RGBA',(512,512))
                for role in frame['base_draw_order']:
                    key=frame['assets'][role];metadata=index['assets'][key]
                    path=store.resolve(key,metadata)
                    self.assertNotIn('-intake-',metadata['source_reference'])
                    with Image.open(path)as image:merged.alpha_composite(image)
                    self.assertTrue((folder/'derived/SW'/role/f'{frame["index"]:03}.png').is_file())
                with Image.open(root/'inputs'/f'{frame["index"]:03}'/'master.png')as master:
                    self.assertEqual(merged.tobytes(),master.tobytes())
            self.assertFalse(list((base/'cutouts').glob('.job-intake-*')))
            self.assertEqual((cas/'index.json.tmp').read_bytes(),b'preserve-old-temp-file')

    def test_changed_source_is_not_overwritten_or_published(self):
        with self.fixture()as(root,base,cas,manifest):
            before=snapshot(cas);register=importer.register;changed=[]
            source=root/'inputs/000/BodyCostume.png'
            def change_after_first_read(*args,**kwargs):
                result=register(*args,**kwargs)
                if not changed:
                    Image.new('RGBA',(512,512),(99,88,77,255)).save(source);changed.append(source.read_bytes())
                return result
            with patch.object(importer,'register',side_effect=change_after_first_read):
                with self.assertRaisesRegex(ValueError,'Input changed'):
                    importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(cas),before)
            self.assertEqual(source.read_bytes(),changed[0])

    def test_existing_publication_lock_is_never_deleted(self):
        with self.fixture()as(root,base,cas,manifest):
            (cas/'.cutout-import.lock').write_bytes(b'prior-active-or-stale-lock')
            before=snapshot(root)
            with self.assertRaisesRegex(ValueError,'publication lock'):
                importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(root),before)

    def test_boolean_pose_index_is_not_treated_as_frame_one(self):
        with self.fixture()as(root,base,cas,manifest):
            document=json.loads(manifest.read_text());document['frames'][1]['index']=True
            manifest.write_text(json.dumps(document));before=snapshot(root)
            with self.assertRaisesRegex(ValueError,'pose record types'):
                importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(root),before)

    def test_all_frames_empty_required_slot_is_rejected_after_private_staging(self):
        with self.fixture()as(root,base,cas,manifest):
            document=json.loads(manifest.read_text())
            for record in document['frames']:
                path=root/'inputs'/record['parts']['Weapon']
                with Image.open(path)as image:mask=np.asarray(image)[:,:,3]>0
                master=root/'inputs'/record['master']
                with Image.open(master)as image:pixels=np.array(image)
                pixels[mask]=0;Image.fromarray(pixels).save(master)
                Image.new('RGBA',(512,512)).save(path)
                record['occlusion_reasons']={'Weapon':'fixture-occluded-in-this-frame'}
            manifest.write_text(json.dumps(document));before=snapshot(root)
            with self.assertRaisesRegex(ValueError,'entirely empty required art slot'):
                importer.import_job('job',manifest)
            self.assert_no_intake(base);self.assertEqual(snapshot(root),before)


if __name__=='__main__':unittest.main()
