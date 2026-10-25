"""Replace one complete head while retaining a native action's body and weapon.

Only recorded rigid head matrices are accepted. No torso edits, motion fitting,
frame-dependent scale, or source file mutation is performed.
"""
import argparse
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
from build_occluded_underlays import composite,sha
from render_segmented_mage_action import warp_affine


def validate_rigid(matrix):
    matrix=np.asarray(matrix,float)
    if matrix.shape!=(2,3)or not np.isfinite(matrix).all():raise ValueError('Finite rigid head matrix required')
    if not np.allclose(matrix[:,:2].T@matrix[:,:2],np.eye(2),atol=1e-9)or not np.isclose(np.linalg.det(matrix[:,:2]),1,atol=1e-9):
        raise ValueError('Replacement head cannot be stretched or reflected')
    return matrix


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','motion','head','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh head variant')
    public=json.loads((a.source/'receipt.json').read_text());motion=json.loads((a.motion/'receipt.json').read_text())
    if public['status']!='LAYERED_NATIVE_ACTION_STUDY'or public['source_receipt_sha256']!=sha(a.motion/'receipt.json'):raise ValueError('Head motion differs from public source')
    head=Image.open(a.head).convert('RGBA')
    if head.size!=(1536,1536):raise ValueError('Replacement head must use the canonical native canvas')
    frozen={str(path):sha(path)for path in [a.head,a.source/'receipt.json',a.motion/'receipt.json']}
    yy,xx=np.mgrid[:1536,:1536].astype(np.float32);a.output.mkdir(parents=True);rows=[];previews=[]
    for row,m in zip(public['frames'],motion['frames'],strict=True):
        i=row['index']
        if i!=m['index']:raise ValueError('Head pose indices differ')
        matrix=validate_rigid(m['transforms']['HeadHair']);parts={};hashes={}
        for role in public['render_order']:
            folder=a.output/role;folder.mkdir(exist_ok=True);target=folder/f'{i:03}.png'
            if role=='HeadHair':
                parts[role]=warp_affine(head,matrix,xx,yy);parts[role].save(target)
            else:
                source=a.source/role/f'{i:03}.png'
                if sha(source)!=row['sha256'][role]:raise ValueError('Reusable body or weapon changed')
                shutil.copyfile(source,target);parts[role]=Image.open(target).convert('RGBA')
            hashes[role]=sha(target)
        master=composite([parts[n]for n in public['render_order']]);folder=a.output/'Master';folder.mkdir(exist_ok=True);path=folder/f'{i:03}.png';master.save(path);hashes['Master']=sha(path)
        rows.append({**row,'sha256':hashes,'body_and_weapon_reused_exactly':True})
        bg=Image.new('RGBA',master.size,'#aaa');bg.alpha_composite(master);previews.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
    if any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Head variant source changed')
    previews[0].save(a.output/'continuous-casting.gif',save_all=True,append_images=previews[1:],duration=80,loop=0)
    result={**public,'frames':rows,'replacement_head':str(a.head),'variant_inputs_sha256':frozen,'implementation_sha256':sha(__file__),'runtime_admitted':False}
    (a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    replay=a.output/'replay';replay.mkdir()
    for name in ['replace_native_action_head.py','render_segmented_mage_action.py','derive_bounded_hold_parts.py','build_occluded_underlays.py']:
        shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'frames':len(rows),'body_and_weapon_reused_exactly':True,'rigid_head_only':True}))


if __name__=='__main__':main()
