"""Translate complete same-frame layer sets onto observed source pelvis anchors.

No image rescaling, body deformation, smoothing or per-layer registration.
Input annotations remain explicit and independently reviewable.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from build_four_direction_attack_review import PARTS, DIRECTIONS, previews, package_sheets


def register(source, destination, guides):
    annotations=json.loads((destination/'registration-annotations.json').read_text())
    assembly=json.loads((source/'assembly-audit.json').read_text())
    reports=[]
    for direction in DIRECTIONS:
        src=source/direction; dst=destination/direction; dst.mkdir(exist_ok=True)
        packing=json.loads((src/'assembly.json').read_text())
        guide=json.loads((guides/direction/'manifest.json').read_text())['frames']
        new_annotations=json.loads((src/'annotations.generated.json').read_text())
        for i,entry in enumerate(packing['frames']):
            observed=np.array(annotations['views'][direction][i],float)
            target=np.array(guide[entry['source_frame']]['landmarks']['pelvis'])*.5
            delta=np.rint(target-observed).astype(int)
            for part in ['Master']+PARTS:
                im=Image.open(src/part/f'{i:03d}.png').convert('RGBA')
                out=Image.new('RGBA',im.size);out.alpha_composite(im,tuple(delta))
                if np.array(im.getchannel('A')).sum() != np.array(out.getchannel('A')).sum():
                    raise ValueError(f'Clipping: {direction} {i} {part}')
                folder=dst/part;folder.mkdir(exist_ok=True);out.save(folder/f'{i:03d}.png')
            for key in ['head_seed','weapon_grip','weapon_tip','weapon_guard']:
                new_annotations['frames'][i][key]=(np.array(new_annotations['frames'][i][key])+delta).tolist()
            entry['registration_translation']=delta.tolist()
            error=float(np.linalg.norm(observed+delta-target))
            reports.append({'direction':direction,'frame':i,'source_frame':entry['source_frame'],'observed_pelvis':observed.tolist(),'source_target':target.tolist(),'translation':delta.tolist(),'rounding_residual_px':error})
            merged=Image.new('RGBA',(512,512))
            for part in ['BodyCostume','HeadHair','Weapon']:merged.alpha_composite(Image.open(dst/part/f'{i:03d}.png'))
            if not np.array_equal(np.array(merged),np.array(Image.open(dst/'Master'/f'{i:03d}.png'))):raise ValueError('Recomposition mismatch')
        (dst/'assembly.json').write_text(json.dumps(packing,indent=2)+'\n')
        (dst/'annotations.generated.json').write_text(json.dumps(new_annotations,indent=2)+'\n')
    assembly['classification']='SkillOverhead'
    assembly['registration']='manual pelvis to matching fixed-camera source pelvis, 1024→512 coordinate scale; integer whole-frame translation only'
    (destination/'assembly-audit.json').write_text(json.dumps(assembly,indent=2)+'\n')
    (destination/'registration-audit.json').write_text(json.dumps({'action':'SkillOverhead','source_scale':.5,'frames':reports,'maximum_rounding_residual_px':max(r['rounding_residual_px'] for r in reports),'recomposition_mismatched_pixels':0,'status':'REGISTERED_REVIEW_NOT_RUNTIME_APPROVAL','limitations':['Manual pelvis anchors are approximate, not independent ground truth.','Translation fixes packing drift, not anatomy or pose drift inside generated artwork.','Existing NE recovery blade foreshortening remains.']},indent=2)+'\n')
    previews(destination);package_sheets(destination)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--guides',type=Path,required=True);a=p.parse_args();register(a.source,a.output,a.guides)
