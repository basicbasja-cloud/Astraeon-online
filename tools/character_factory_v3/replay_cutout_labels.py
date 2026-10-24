"""Rebuild frozen visible cutouts from masters and labels without SAM2 or AI.

Checks the exact persisted RGBA and PNG hashes for every selected output role.
This validates reproducibility, not semantic boundaries or animation quality.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from cutout_asset_store import import_frame
from track_visible_cutouts import pin_inputs,verify_inputs,sha

ROLES=['BodyCostume','HeadHair','Weapon','BackAccessory','Headgear','WeaponHandOccluder']


def replay(receipt_path,masters,output):
    if output.exists():raise ValueError('Choose a fresh rebuild destination')
    receipt=json.loads(receipt_path.read_text());records=receipt['frames'];source=receipt_path.parent
    if not records or len({r['index']for r in records})!=len(records):raise ValueError('Missing or duplicate source frames')
    pinned=pin_inputs([receipt_path,Path(__file__)]+[path for r in records for path in [masters/f"{r['index']:03d}.png",source/'labels'/f"{r['index']:03d}.png",*[source/role/f"{r['index']:03d}.png"for role in r['part_sha256']]]])
    output.mkdir(parents=True);checks=[]
    for r in records:
        i=r['index'];master=masters/f'{i:03d}.png';labels=source/'labels'/f'{i:03d}.png'
        if sha(master)!=r['master_sha256'] or sha(labels)!=r['labels_sha256']:raise ValueError('Frozen master/labels changed')
        a=np.array(Image.open(master));ids=np.array(Image.open(labels))
        if ids.shape!=a.shape[:2] or np.any(~np.isin(ids,[0,1,2,3,4,5,6])) or np.any((a[:,:,3]==0)&(ids!=0)):raise ValueError('Invalid visible ownership labels')
        targets={role:output/role/f'{i:03d}.png'for role in ROLES};import_frame(master,labels,targets)
        for role,digest in r['part_sha256'].items():
            frozen=source/role/f'{i:03d}.png'
            if role not in targets or sha(frozen)!=digest:raise ValueError('Frozen source part changed: '+role)
            original=np.array(Image.open(frozen).convert('RGBA'));rebuilt=np.array(Image.open(targets[role]).convert('RGBA'))
            if original.shape!=rebuilt.shape or not np.array_equal(original,rebuilt):raise ValueError('Rebuilt RGBA pixels differ: '+role)
            actual_sha=sha(targets[role])
            checks.append({'index':i,'role':role,'frozen_png_sha256':digest,'rebuilt_png_sha256':actual_sha,'png_bytes_identical':actual_sha==digest,
                           'rgba_sha256':hashlib.sha256(rebuilt.tobytes()).hexdigest(),'matches_frozen_export':True})
    verify_inputs(pinned)
    result={'status':'EXACT_FROZEN_CUTOUT_REPLAY_VERIFIED','frames':len(records),'role_checks':checks,
            'receipt_sha256':sha(receipt_path),'implementation_sha256':sha(Path(__file__)),
            'requires_sam2':False,'requires_image_generation':False,'runtime_admitted':False,'visual_approval_implied':False}
    (output/'replay-receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['receipt','masters','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=replay(a.receipt,a.masters,a.output);print(json.dumps({'frames':r['frames'],'exact_role_checks':len(r['role_checks']),'requires_sam2':False}))
