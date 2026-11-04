"""Normalize one illustrated rig template before any animation is derived.

One recorded isotropic art calibration is reused by every future frame. This
tool refuses animation sheets; it never fits per-frame silhouettes or changes
the Blender camera. Raw generation, viewport and guide references stay frozen.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

import derive_bounded_hold_parts
import normalize_fixed_viewport_batch


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def calibrate(image,scale,offset):
    if not .5<=scale<=1.5 or len(offset)!=2 or not np.isfinite(offset).all() or max(abs(v) for v in offset)>256:
        raise ValueError('Choose a finite bounded static art calibration')
    yy,xx=np.mgrid[:image.height,:image.width].astype(np.float32)
    sx=(xx+.5-offset[0])/scale-.5
    sy=(yy+.5-offset[1])/scale-.5
    return derive_bounded_hold_parts.resample_rgba(image,sy,sx)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['image','viewport','guide','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--direction',default='NE')
    parser.add_argument('--scale',type=float,required=True)
    parser.add_argument('--offset',type=float,nargs=2,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Choose a fresh static template output')
    recipe=json.loads(args.viewport.read_text())
    if recipe['grid']!=[1,1] or len(recipe['source_pose_indices'])!=1 or recipe['source_size']!=[1536,1536]:
        raise ValueError('Only a single native 1536px template is supported')
    index=recipe['source_pose_indices'][0]
    capture=json.loads((args.guide/'pilot-receipt.json').read_text())
    row=capture['views'][args.direction]['frames'][index]
    reference=args.guide/args.direction/f'{index:03d}.png'
    if sha(reference)!=row['image_sha256']:
        raise ValueError('Native template reference changed')
    frames,normalization=normalize_fixed_viewport_batch.normalize_batch(Image.open(args.image),recipe)
    if normalization['production_blockers']:
        raise ValueError('Raw single template touches viewport edges')
    result=calibrate(frames[0],args.scale,args.offset)
    alpha=np.array(result.getchannel('A'))>16
    if not alpha.any() or alpha[0].any() or alpha[-1].any() or alpha[:,0].any() or alpha[:,-1].any():
        raise ValueError('Empty or clipped calibrated template')
    args.output.mkdir(parents=True)
    (args.output/'Master').mkdir()
    result.save(args.output/'Master'/f'{index:03d}.png')
    frames[0].save(args.output/'before-calibration.png')
    dependencies={module.__name__:Path(module.__file__) for module in [derive_bounded_hold_parts,normalize_fixed_viewport_batch]}
    scripts=args.output/'replay';scripts.mkdir()
    shutil.copyfile(__file__,scripts/'normalize_single_art_template.py')
    for name,path in dependencies.items():shutil.copyfile(path,scripts/(name+'.py'))
    report={'status':'SINGLE_ART_TEMPLATE_CALIBRATED_NOT_ADMITTED','direction':args.direction,'source_pose_index':index,
            'normalization':normalization,'static_art_scale':args.scale,'static_art_offset':args.offset,
            'per_frame_fitting':False,'camera_modified':False,'calibration_reused_by_all_derived_frames':True,
            'input_sha256':{str(path):sha(path)for path in [args.image,args.viewport,args.guide/'pilot-receipt.json',reference]},
            'implementation_sha256':sha(__file__),'dependency_sha256':{name:sha(path)for name,path in dependencies.items()},
            'master_sha256':sha(args.output/'Master'/f'{index:03d}.png'),
            'source_pose_alignment_approved':False,'semantic_cutouts_approved':False,'runtime_admitted':False}
    (args.output/'normalization.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'templates':1,'static_scale':args.scale,'static_offset':args.offset,'per_frame_fitting':False}))


if __name__=='__main__':main()
