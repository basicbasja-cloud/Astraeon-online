"""Freeze a draft four-view head variant and real separated sprite sheets.

The parent body, blade, gloves and FX stay in their original pose. Existing gold
collar pixels change ownership from the old head to the body; no new anatomy is
invented. This is a variant review package, not an admitted class/sex package.
"""
import argparse,json,os
from pathlib import Path
import numpy as np
from PIL import Image
from track_visible_cutouts import pin_inputs,verify_inputs,sha

ORDER=['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder']


def package(review,source,output):
    if output.exists():raise ValueError('Choose a fresh package destination')
    receipt_path=review/'receipt.json';receipt=json.loads(receipt_path.read_text());rows=receipt['frames']
    expected={(d,i)for d in ['SW','NW','NE','SE']for i in range(16)}
    if {(r['direction'],r['index'])for r in rows}!=expected or len(rows)!=64:raise ValueError('Incomplete four-view variant')
    inputs=[receipt_path,Path(__file__)]+[review/r['direction']/role/f"{r['index']:03d}.png"for r in rows for role in ['HeadHair','CollarOwnershipPatch','Master']]
    inputs += [Path(p['path'])for r in rows for p in r['unchanged_reused_parts'].values()]
    pinned=pin_inputs(inputs);output.mkdir(parents=True);records=[];sheets={}
    for r in rows:
        d=r['direction'];i=r['index'];folder=output/d;body=Image.open(source/d/'BodyCostume'/f'{i:03d}.png').convert('RGBA');patch=Image.open(review/d/'CollarOwnershipPatch'/f'{i:03d}.png').convert('RGBA');body.alpha_composite(patch)
        (folder/'BodyCostume').mkdir(parents=True,exist_ok=True);body_path=folder/'BodyCostume'/f'{i:03d}.png';body.save(body_path)
        head_path=review/d/'HeadHair'/f'{i:03d}.png'
        parts={'BodyCostume':body_path,'HeadHair':head_path,**{role:source/d/role/f'{i:03d}.png'for role in ['Weapon','WeaponHandOccluder','WeaponLightBack','WeaponLightFront']}}
        composed=Image.new('RGBA',(768,768))
        for role in ORDER:
            im=Image.open(parts[role]).convert('RGBA');composed.alpha_composite(im)
            key=d,role
            if key not in sheets:sheets[key]=Image.new('RGBA',(3072,3072))
            sheets[key].paste(im,((i%4)*768,(i//4)*768))
        actual=np.array(composed);wanted=np.array(Image.open(review/d/'Master'/f'{i:03d}.png').convert('RGBA'));actual[actual[:,:,3]==0]=0;wanted[wanted[:,:,3]==0]=0
        changed=int(np.count_nonzero(np.any(actual!=wanted,axis=2)))
        if changed:raise ValueError('Variant layer recomposition differs')
        records.append({'direction':d,'index':i,'source_action':r['source_action'],'source_frame':r['source_frame'],'parts':{role:{'file':os.path.relpath(path,output),'sha256':sha(path)}for role,path in parts.items()},'changed_visible_pixels':changed,'head_library_entry':r['library_entry'],'head_slot_author_px':r['target_neck_author_px']})
    sheet_rows=[]
    for (d,role),im in sheets.items():
        path=output/d/(role+'-sheet.png');im.save(path);sheet_rows.append({'direction':d,'role':role,'file':str(path.relative_to(output)),'sha256':sha(path),'frame_size':[768,768],'grid':[4,4]})
    verify_inputs(pinned)
    result={'status':'REPRODUCIBLE_DRAFT_HEAD_VARIANT_NOT_ADMITTED','parent_character':'swordsman-male-patch001','variant_design':'female silver ponytail on shared covered starter armor','guide_job':receipt['guide_job'],'review_receipt_sha256':sha(receipt_path),'implementation_sha256':sha(Path(__file__)),'layer_draw_order':ORDER,'frames':records,'sheets':sheet_rows,'body_motion_and_scale_changed':False,'collar_pixels_reassigned_from_existing_head':True,'hidden_surfaces_authored':False,'semantic_neck_and_arm_review_complete':False,'new_female_base_paint_job_imported':False,'runtime_admitted':False}
    (output/'variant.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['review','source','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=package(a.review,a.source,a.output);print(json.dumps({'frames':len(r['frames']),'separated_sprite_sheets':len(r['sheets']),'all_recomposition_errors':0}))
