"""Replay the pre-fix failure and compare successful old/new intake identities.

Runs only inside disposable synthetic fixtures. No production art is imported.
"""
import argparse
import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import re
import subprocess
import sys
import types
from unittest.mock import patch

from PIL import Image
from test_cutout_import_transaction import CutoutImportTransactionTests,importer,store,snapshot,ROOT


def prior_modules(ref):
    if not re.fullmatch('[0-9a-f]{7,40}',ref):raise ValueError('Use a pinned hexadecimal baseline commit')
    modules=[];digests={}
    for filename in ('cutout_asset_store.py','import_patch001_cutouts.py'):
        source=subprocess.run(['git','show',f'{ref}:tools/character_factory_v3/{filename}'],cwd=ROOT,
                              check=True,capture_output=True).stdout
        module=types.ModuleType('prior_'+filename.removesuffix('.py'))
        module.__file__=str(ROOT/'tools/character_factory_v3'/filename)
        if modules:
            with patch.dict(sys.modules,{'cutout_asset_store':modules[0]}):
                exec(compile(source,module.__file__,'exec'),module.__dict__)
        else:exec(compile(source,module.__file__,'exec'),module.__dict__)
        modules.append(module);digests[filename]=hashlib.sha256(source).hexdigest()
    return modules[0],modules[1],digests


def run(ref):
    old_store,old_importer,old_hashes=prior_modules(ref);fixture=CutoutImportTransactionTests()
    cases={};success={}
    for name,implementation in (('before',old_importer),('after',importer)):
        with fixture.fixture()as(root,base,cas,manifest):
            if name=='before':
                old_store.ROOT=root;old_store.STORE=cas
                old_importer.ROOT=root;old_importer.BASE=base;old_importer.STORE=cas
                old_importer.receipt_valid=lambda job:True
            before=snapshot(cas);Image.new('RGBA',(512,512)).save(root/'inputs/001/Weapon.png')
            try:implementation.import_job('job',manifest)
            except ValueError as exc:error=str(exc)
            else:raise AssertionError('Broken second frame must fail')
            cases[name]={'error':error,'partial_import_folder_left':(base/'cutouts/job').exists(),
                         'new_shared_object_files_left':len(set(snapshot(cas))-set(before)),
                         'original_index_unchanged':(cas/'index.json').read_bytes()==before['index.json']}
        with fixture.fixture(labels=True)as(root,base,cas,manifest):
            if name=='before':
                old_store.ROOT=root;old_store.STORE=cas
                old_importer.ROOT=root;old_importer.BASE=base;old_importer.STORE=cas
            with redirect_stdout(io.StringIO()):implementation.import_job('job',manifest)
            bindings=(base/'cutouts/job/bindings.json').read_bytes();index=(cas/'index.json').read_bytes()
            success[name]={'bindings_sha256':hashlib.sha256(bindings).hexdigest(),
                           'index_sha256':hashlib.sha256(index).hexdigest(),
                           'frames':len(json.loads(bindings)['frames']),
                           'assets':len(json.loads(index)['assets']),
                           'receipt':json.loads((base/'cutouts/job/import-receipt.json').read_text())}
    assert cases['before']['partial_import_folder_left']and cases['before']['new_shared_object_files_left']>0
    assert not cases['after']['partial_import_folder_left']and cases['after']['new_shared_object_files_left']==0
    assert success['before']['bindings_sha256']==success['after']['bindings_sha256']
    assert success['before']['index_sha256']==success['after']['index_sha256']
    assert not success['after']['receipt']['owner_approved']and not success['after']['receipt']['runtime_admitted']
    return {'status':'INTAKE_ROLLBACK_REGRESSION_REPRODUCED_AND_FIXED_NOT_ART_APPROVAL',
            'baseline_commit':ref,'baseline_implementation_sha256':old_hashes,
            'current_implementation_sha256':{name:hashlib.sha256((ROOT/'tools/character_factory_v3'/name).read_bytes()).hexdigest()for name in old_hashes},
            'replay_implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'late_validation_failure':cases,
            'successful_fixture_binding_ids_and_metadata_unchanged':True,
            'successful_fixture':success['after'],
            'synthetic_fixture_only':True,'new_art_or_gameplay_approval':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--baseline-ref',default='ad0bf2b')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists()or args.output.is_symlink():raise ValueError('Choose a fresh evidence file')
    result=run(args.baseline_ref);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'failure_comparison':result['late_validation_failure']}))
