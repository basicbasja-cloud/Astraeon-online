import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import adopt_hit_render_snapshot as adoption
import patch001_factory as factory


def files(root):return{str(p.relative_to(root)):p.read_bytes()for p in root.rglob('*')if p.is_file()}


class HitSnapshotAdoptionTests(unittest.TestCase):
    def fixture(self,root):
        base=root/'factory';base.mkdir();identities=base/'identities';identities.mkdir()
        geometry={'source_actions':['Hit_Chest'],'source_file':'source.glb','source_sha256':'a'*64,
                  'renderer_sha256':factory.filehash(factory.TOOLS/'render_patch001_guides.py'),
                  'frames':12,'loop':False,'resolution':1536,'weapon':'sword'}
        old_id=factory.digest(geometry)[:20]
        guide={'id':old_id,**geometry,'directions':['SW'],'uses':['Swordsman/Hit']}
        characters=[];paint={}
        for i,sex in enumerate(('male','female')):
            seed=identities/f'{sex}-seed.png';sheet=identities/f'{sex}-turnaround.png'
            Image.new('RGBA',(2,2),(10+i,40,60,255)).save(seed)
            Image.new('RGBA',(2,2),(20+i,40,60,255)).save(sheet)
            ref=identities/'views'/sex;ref.mkdir(parents=True)
            (ref/'receipt.json').write_text(json.dumps({'source_sha256':factory.filehash(sheet),'head_crop_revision':2}))
            character={'id':f'swordsman-{sex}','direction_reference_sheet':str(sheet.relative_to(root))}
            characters.append(character)
            key=factory.digest({'identity':factory.filehash(seed),'direction_identity':factory.filehash(sheet),
                                'direction_crop_revision':2,'fit':sex,'guide':old_id})[:20]
            paint[key]={'id':key,'character':character['id'],'guide_job':old_id,'identity_reference':str(seed.relative_to(root)),
                        'identity_sha256':factory.filehash(seed),'fit_id':sex,'directions':['SW'],'frame_count':12,
                        'actions':['Hit'],'status':'MISSING_PAINTED_MASTERS_AND_LABELS',
                        'approval':{'owner_approved':False,'runtime_admitted':False,'custom_note':'preserve'},'custom_data':'preserve'}
        config={'classes':{'Swordsman':{'actions':{'Hit':{'frames':12,'owner_approved':False},'Walk':{'frames':16}}}},
                'characters':characters,'unrelated':'preserve'}
        ledger={'guide_jobs':{old_id:guide,'other':{'id':'other','unchanged':True}},
                'action_guide_bindings':{'Swordsman/Hit':old_id,'Swordsman/Walk':'other'},
                'paint_jobs':{**paint,'other':{'guide_job':'other','unchanged':True}},'requested_action_instances':3}
        (base/'factory.json').write_text(json.dumps(config,indent=2)+'\n');(base/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
        return base,config,ledger

    def test_proposal_changes_only_one_guide_and_two_pending_paint_jobs(self):
        with tempfile.TemporaryDirectory()as temporary:
            root=Path(temporary);base,config,ledger=self.fixture(root);before=files(root)
            documents,job,proof=adoption.proposal(base,root)
            self.assertEqual(files(root),before)
            self.assertEqual(proof['unrelated_guide_jobs_unchanged'],1);self.assertEqual(proof['unrelated_paint_jobs_unchanged'],1)
            self.assertEqual(len(proof['paint_job_mapping']),2);self.assertEqual(proof['logical_action_instances'],3)
            changed=documents[base/'ledger.json'];self.assertEqual(changed['paint_jobs']['other'],ledger['paint_jobs']['other'])
            for key in proof['paint_job_mapping'].values():
                self.assertEqual(changed['paint_jobs'][key]['custom_data'],'preserve')
                self.assertEqual(changed['paint_jobs'][key]['approval']['custom_note'],'preserve')
            self.assertEqual(documents[base/'factory.json']['classes']['Swordsman']['actions']['Walk'],{'frames':16})

    def test_existing_artwork_and_intakes_are_not_silently_rebound(self):
        for mode in ('approved','intake','draft'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as temporary:
                root=Path(temporary);base,config,ledger=self.fixture(root);key=next(k for k in ledger['paint_jobs']if k!='other')
                if mode=='approved':ledger['paint_jobs'][key]['approval']['owner_approved']=True
                elif mode=='draft':ledger['paint_jobs'][key]['status']='DRAFT_MASTERS_EXIST'
                else:(base/'cutouts'/key).mkdir(parents=True)
                (base/'ledger.json').write_text(json.dumps(ledger));before=files(root)
                with self.assertRaises(ValueError):adoption.proposal(base,root)
                self.assertEqual(files(root),before)

    def test_changed_identity_prevents_rebinding(self):
        with tempfile.TemporaryDirectory()as temporary:
            root=Path(temporary);base,_,_=self.fixture(root)
            Image.new('RGBA',(2,2),'red').save(base/'identities/male-seed.png');before=files(root)
            with self.assertRaisesRegex(ValueError,'identity references changed'):adoption.proposal(base,root)
            self.assertEqual(files(root),before)

    def test_missing_verified_capture_never_writes_planning_files(self):
        with tempfile.TemporaryDirectory()as temporary:
            root=Path(temporary);base,_,_=self.fixture(root);before=files(root)
            with patch.object(factory,'receipt_valid',return_value=False):
                with self.assertRaisesRegex(ValueError,'verified Hit snapshot capture'):adoption.adopt(base,root,root/'missing')
            self.assertEqual(files(root),before)

    def test_write_failure_restores_prior_plan_and_removes_only_new_job_files(self):
        with tempfile.TemporaryDirectory()as temporary:
            root=Path(temporary);base,_,_=self.fixture(root);capture=root/'capture';capture.mkdir();(capture/'manifest.json').write_text('{}')
            before=files(root);replace=adoption.replace_bytes;count=[]
            def fail_fourth(path,data):
                count.append(path)
                if len(count)==4:raise OSError('simulated planning publication failure')
                return replace(path,data)
            with patch.object(factory,'receipt_valid',return_value=True),patch.object(adoption,'replace_bytes',side_effect=fail_fourth):
                with self.assertRaises(OSError):adoption.adopt(base,root,capture)
            self.assertEqual(files(root),before)

    def test_adoption_is_idempotent_and_keeps_unrelated_work(self):
        with tempfile.TemporaryDirectory()as temporary:
            root=Path(temporary);base,_,_=self.fixture(root);capture=root/'capture';capture.mkdir();(capture/'manifest.json').write_text('{}')
            with patch.object(factory,'receipt_valid',return_value=True):
                first=adoption.adopt(base,root,capture);before=files(root)
                with patch.object(adoption,'replace_bytes')as write:second=adoption.adopt(base,root,capture)
                write.assert_not_called()
            self.assertFalse(first['already_current']);self.assertTrue(second['already_current']);self.assertEqual(files(root),before)


if __name__=='__main__':unittest.main()
