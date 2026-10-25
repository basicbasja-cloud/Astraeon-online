"""Animate overlapping authored underlays without flattening away hidden pixels.

Uses a verified bounded native-hold capture. Every layer receives the same
source joint field; the master is recomposed from those independent layers.
Only small native hold motions are supported, not attacks or locomotion.
"""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

import derive_bounded_hold_parts as motion
from build_occluded_underlays import composite


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['template','motion','guide','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--head',type=Path,help='Optional separately authored native-canvas HeadHair replacement')
    parser.add_argument('--head-placement',type=Path,help='Pinned static template placement for the replacement head')
    args=parser.parse_args()
    if bool(args.head)!=bool(args.head_placement):raise ValueError('Replacement head requires its authored static placement')
    if args.output.exists():raise ValueError('Choose a fresh layered hold output')
    certificate=json.loads((args.motion/'receipt.json').read_text())
    template=json.loads((args.template/'receipt.json').read_text())
    guide=json.loads((args.guide/'pilot-receipt.json').read_text())
    if certificate['status']!='BOUNDED_NATIVE_HOLD_REUSE_NOT_ADMITTED' or template['status']!='OPAQUE_OCCLUDED_UNDERLAY_STUDY':
        raise ValueError('Expected native bounded motion and authored underlay receipts')
    if motion.sha(args.motion/'renderer-source.py')!=certificate['implementation_sha256']:
        raise ValueError('Motion implementation snapshot changed')
    if motion.sha(motion.__file__)!=certificate['implementation_sha256']:
        raise ValueError('Use the exact certified motion implementation')
    for name,digest in certificate['input_sha256'].items():
        if motion.sha(name)!=digest:raise ValueError('Motion input changed')
    for name,digest in template['input_sha256'].items():
        if motion.sha(name)!=digest:raise ValueError('Authored underlay input changed')
    direction=certificate['direction']
    if template['direction']!=direction or template['index']!=certificate['source_template_pose']:
        raise ValueError('Template camera/pose differs from motion')
    # The underlay recipe is based on the same posed source, not another clip.
    guide_path=args.guide/'pilot-receipt.json'
    if certificate['input_sha256'].get(str(guide_path))!=motion.sha(guide_path):
        raise ValueError('Guide is not a pinned motion input')
    roles=template['render_order']
    if roles!=['WeaponBack','BodyCostume','HeadHair','Weapon','WeaponHandOccluder']:
        raise ValueError('Unsupported authored layer order')
    paths={r:args.template/r/'000.png' for r in roles}
    for role,digest in template['output_sha256'].items():
        if motion.sha(paths[role])!=digest:raise ValueError('Authored underlay output changed')
    images={r:Image.open(p).convert('RGBA') for r,p in paths.items()}
    if any(im.size!=(motion.SIZE,motion.SIZE)for im in images.values()):raise ValueError('Native layer canvas differs')
    if composite(list(images.values())).tobytes()!=Image.open(args.template/'Master.png').convert('RGBA').tobytes():
        raise ValueError('Underlay template does not reconstruct its master')
    # These two checks bind the underlay to the exact input pose of the verified
    # motion; a similarly named head or differently scaled body is insufficient.
    for role in ['HeadHair','WeaponHandOccluder']:
        candidates=[p for p in certificate['input_sha256']if p.endswith('/'+role+'/000.png')]
        if len(candidates)!=1 or template['input_sha256'].get(candidates[0])!=certificate['input_sha256'][candidates[0]]:
            raise ValueError('Underlay was not built from the certified motion template')
    frozen={str(p):motion.sha(p)for p in [args.template/'receipt.json',args.template/'Master.png',args.motion/'receipt.json',guide_path,*paths.values()]}
    if args.head:
        placement=json.loads(args.head_placement.read_text())
        if placement.get('direction')!=direction or placement.get('index')!=template['index'] or placement.get('per_frame_fitting') is not False:
            raise ValueError('Replacement head placement differs from source pose')
        replacement=Image.open(args.head).convert('RGBA')
        if replacement.size!=(motion.SIZE,motion.SIZE):raise ValueError('Replacement head must use the native canvas')
        if not replacement.getchannel('A').getbbox():raise ValueError('Replacement head is empty')
        images['HeadHair']=replacement
        frozen.update({str(p):motion.sha(p)for p in [args.head,args.head_placement]})
    view=guide['views'][direction];base=view['frames'][certificate['source_template_pose']]
    source=motion.controls(base,view['camera'])
    yy,xx=np.mgrid[:motion.SIZE,:motion.SIZE].astype(np.float32)
    args.output.mkdir(parents=True);records=[];previews=[]
    for row,verified in zip(view['frames'],certificate['frames'],strict=True):
        if row['index']!=verified['index']:raise ValueError('Native pose sequence changed')
        field,metrics,_=motion.inverse_field(source,motion.controls(row,view['camera']))
        for key,value in metrics.items():
            if abs(value-verified['deformation'][key])>1e-7:raise ValueError('Native deformation differs from verified capture')
        dx,dy=[ndimage.map_coordinates(field[:,:,axis],[((yy+.5)/motion.SPACING),((xx+.5)/motion.SPACING)],order=1,prefilter=False).astype(np.float32)for axis in range(2)]
        warped={r:motion.resample_rgba(im,yy+dy,xx+dx)for r,im in images.items()}
        warped['Master']=composite([warped[r]for r in roles])
        hashes={}
        for role,image in warped.items():
            folder=args.output/role;folder.mkdir(exist_ok=True);path=folder/f"{row['index']:03d}.png"
            image.save(path);hashes[role]=motion.sha(path)
        records.append({'index':row['index'],'source_action':row['source_action'],'source_frame':row['source_frame'],'sha256':hashes,'deformation':metrics})
        bg=Image.new('RGBA',(motion.SIZE,motion.SIZE),'#eee');bg.alpha_composite(warped['Master'])
        previews.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
        print('LAYERED_NATIVE_HOLD',row['index'],flush=True)
    if any(motion.sha(p)!=digest for p,digest in frozen.items()):raise ValueError('Layered input changed during rendering')
    previews[0].save(args.output/'layered-native-loop.gif',save_all=True,append_images=previews[1:],duration=80,loop=0)
    receipt={'status':'LAYERED_NATIVE_HOLD_STUDY','direction':direction,'render_order':roles,
             'input_sha256':frozen,'implementation_sha256':motion.sha(__file__),
             'dependencies_sha256':{'derive_bounded_hold_parts.py':motion.sha(motion.__file__),
                                      'build_occluded_underlays.py':motion.sha(Path(__file__).with_name('build_occluded_underlays.py'))},
             'overlapping_hidden_pixels_preserved':True,'per_frame_generation':False,
             'replacement_head':str(args.head)if args.head else None,
             'loop_evidence':certificate['loop_evidence'],'frames':records,
             'semantic_swaps_approved':False,'runtime_admitted':False,'full_character_complete':False}
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    replay=args.output/'replay';replay.mkdir()
    for name in ['derive_layered_native_hold.py','derive_bounded_hold_parts.py','build_occluded_underlays.py']:
        shutil.copyfile(Path(__file__).with_name(name),replay/name)


if __name__=='__main__':main()
