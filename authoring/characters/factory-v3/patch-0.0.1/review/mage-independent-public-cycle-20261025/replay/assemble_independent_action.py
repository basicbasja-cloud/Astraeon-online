"""Assemble complete painted primitives into interchangeable public sprite roles.

The source kit retains hidden shoulders and full sleeves. This step merges body
primitives in their native order, preserving the head and complete prop as
independent layers. It refuses any merge that changes occlusion.
"""
import argparse
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
from build_occluded_underlays import composite,sha

BODY_ORDER=['UpperArmR','ForearmR','HandR','Torso','UpperArmL','ForearmL','HandL']
PUBLIC_ORDER=['Weapon','BodyCostume','HeadHair']


def assemble(parts,original):
    public={'Weapon':parts['Weapon'],'BodyCostume':composite([parts[n]for n in BODY_ORDER]),'HeadHair':parts['HeadHair']}
    master=composite([public[n]for n in PUBLIC_ORDER])
    difference=np.abs(np.array(master).astype(int)-np.array(original).astype(int))
    maximum=int(difference.max())
    if maximum>1:raise ValueError('Public role merge changes native occlusion')
    return public,master,maximum


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh public sprite export')
    receipt=json.loads((a.source/'receipt.json').read_text())
    if receipt['input_kind']!='independently-painted-complete-parts' or receipt['partial_selection']:
        raise ValueError('Complete independently painted native action required')
    expected=['Weapon','UpperArmR','ForearmR','HandR','Torso','UpperArmL','HeadHair','ForearmL','HandL']
    if receipt['render_order']!=expected:raise ValueError('Source primitive occlusion differs')
    a.output.mkdir(parents=True);records=[];previews=[]
    for row in receipt['frames']:
        i=row['index'];parts={}
        for role,digest in row['sha256'].items():
            path=a.source/role/f'{i:03}.png'
            if sha(path)!=digest:raise ValueError('Source painted primitive changed')
            parts[role]=Image.open(path).convert('RGBA')
        public,master,maximum=assemble(parts,parts['Master']);hashes={}
        for role,image in {**public,'Master':master}.items():
            folder=a.output/role;folder.mkdir(exist_ok=True);path=folder/f'{i:03}.png';image.save(path);hashes[role]=sha(path)
        records.append({'index':i,'source_action':row['source_action'],'source_frame':row['source_frame'],
                        'sha256':hashes,'maximum_merge_rounding_difference':maximum})
        bg=Image.new('RGBA',master.size,'#aaa');bg.alpha_composite(master)
        previews.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
    seam={r:Image.open(a.output/r/'000.png').tobytes()==Image.open(a.output/r/f"{records[-1]['index']:03}.png").tobytes()for r in [*PUBLIC_ORDER,'Master']}
    if not all(seam.values()):raise ValueError('Expected a closed native action cycle')
    previews[0].save(a.output/'continuous-casting.gif',save_all=True,append_images=previews[1:],duration=80,loop=0)
    result={'status':'LAYERED_NATIVE_ACTION_STUDY','direction':receipt['direction'],'render_order':PUBLIC_ORDER,'frames':records,
            'source_receipt_sha256':sha(a.source/'receipt.json'),'implementation_sha256':sha(__file__),
            'replacement_head':False,'loop_evidence':{'first_last_rgba_equal':seam,'terminal_frame_cloned':False},
            'independent_source_primitives':9,'hidden_body_and_weapon_preserved':True,'runtime_admitted':False}
    (a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    replay=a.output/'replay';replay.mkdir()
    for name in ['assemble_independent_action.py','build_occluded_underlays.py']:
        shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'frames':len(records),'maximum_merge_rounding_difference':max(r['maximum_merge_rounding_difference']for r in records),'closed_roles':seam}))


if __name__=='__main__':main()
