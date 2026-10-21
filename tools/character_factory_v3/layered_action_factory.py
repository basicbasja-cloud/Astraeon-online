"""Rebuild the owner's registered layered action catalog without provider calls.

python tools/character_factory_v3/layered_action_factory.py --action all
Source sheets, annotations and license evidence are retained inputs. This tool
does not silently generate missing art or admit review assets to runtime.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPO=Path(__file__).resolve().parents[2]
CATALOG=REPO/'authoring/characters/factory-v3/configs/layered_action_catalog.json'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--action',choices=['all','BasicAttack','SkillOverhead'],default='all')
    parser.add_argument('--list',action='store_true')
    args=parser.parse_args();catalog=json.loads(CATALOG.read_text())
    if args.list:
        print(json.dumps(catalog,indent=2));return
    digest=hashlib.sha256((REPO/catalog['source_path']).read_bytes()).hexdigest()
    if digest!=catalog['source_sha256']:raise ValueError('Immutable source GLB digest mismatch')
    if not (REPO/catalog['license_evidence']).is_file():raise ValueError('Missing source license evidence')
    for name,action in catalog['actions'].items():
        if args.action not in ['all',name]:continue
        folder=REPO/action['directory']
        if name=='SkillOverhead':
            command=['register_layered_action.py','--source',action['original_review'],'--output',action['directory'],'--guides',action['guides']]
        else:command=['build_simple_attack_factory.py',action['directory']]
        subprocess.run([sys.executable,str(REPO/'tools/character_factory_v3'/command[0]),*command[1:]],cwd=REPO,check=True)
        subprocess.run([sys.executable,str(REPO/'tools/character_factory_v3/build_four_direction_attack_viewer.py'),str(folder)],cwd=REPO,check=True)
        manifest=json.loads((folder/'sprite-sheets-manifest.json').read_text())
        if manifest['action']!=name:raise ValueError('Export action identity mismatch')
        receipt={'action':name,'source_sha256':digest,'cell_size':catalog['cell_size'],'directions':catalog['directions'],'parts':catalog['parts'],'sheet_checks':manifest['sheet_checks'],'owner_approved':False,'runtime_admitted':False}
        (folder/'factory-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print('ACTION_PACKAGED',name,flush=True)


if __name__=='__main__':main()
