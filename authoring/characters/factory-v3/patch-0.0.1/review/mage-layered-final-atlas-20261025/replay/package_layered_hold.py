"""Pack layered hold studies with native hidden pixels and integer offsets.

This review package exercises the real game's source compositor, not a complete
character definition. Missing classes/actions/directions are never substituted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
from pack_patch001_character import atlas_pages,trimmed_source
from build_occluded_underlays import composite,sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant',nargs=2,action='append',required=True,metavar=('NAME','DIRECTORY'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Choose a fresh layered atlas package')
    names=[v[0]for v in args.variant]
    if len(names)!=len(set(names)):raise ValueError('Duplicate variant name')
    objects=[];lookup={};variants={};inputs={};roles=None;direction=None
    for name,folder in args.variant:
        root=Path(folder);receipt=json.loads((root/'receipt.json').read_text())
        if receipt['status']!='LAYERED_NATIVE_HOLD_STUDY':raise ValueError('Expected a layered native hold study')
        if roles is None:roles=receipt['render_order'];direction=receipt['direction']
        if roles!=receipt['render_order']or direction!=receipt['direction']:raise ValueError('Variant camera/order differs')
        inputs[str(root/'receipt.json')]=sha(root/'receipt.json')
        frames=[]
        for row in receipt['frames']:
            index=row['index'];images={r:Image.open(root/r/f'{index:03d}.png').convert('RGBA')for r in [*roles,'Master']}
            if any(sha(root/r/f'{index:03d}.png')!=row['sha256'][r]for r in images):raise ValueError('Layered native file changed')
            if composite([images[r]for r in roles]).tobytes()!=images['Master'].tobytes():raise ValueError('Layered master does not match its real cutouts')
            references={}
            for role,image in images.items():
                cropped,offset=trimmed_source(image)
                digest=hashlib.sha256(str(cropped.size).encode()+cropped.tobytes()).hexdigest()
                if digest not in lookup:
                    lookup[digest]=len(objects);objects.append(cropped)
                references[role]={'object':lookup[digest],'offset':offset}
            frames.append({'index':index,'duration_ms':80,'layers':references})
        variants[name]={'frames':frames,'replacement_head':receipt['replacement_head'],'loop_evidence':receipt['loop_evidence']}
    args.output.mkdir(parents=True)
    placements={};pages=[]
    for number,(page,items)in enumerate(atlas_pages(objects,limit=2048,padding=2)):
        filename=f'parts-{number:03d}.png';page.save(args.output/filename)
        pages.append({'path':filename,'size':list(page.size),'sha256':sha(args.output/filename)})
        for index,rect in items:placements[index]={'atlasId':str(number),'rect':rect}
    for variant in variants.values():
        for frame in variant['frames']:
            for ref in frame['layers'].values():ref.update(placements[ref.pop('object')])
    report={'status':'NATIVE_LAYERED_REVIEW_ATLAS_NOT_PLAYABLE_CHARACTER','direction':direction,
            'render_order':roles,'variants':variants,'pages':pages,
            'canvas':{'frameWidth':240,'frameHeight':240,'rootAnchorX':120,'rootAnchorY':172,'referenceHeight':88,'compositionWidth':1536,'compositionHeight':1536},
            'input_sha256':inputs,'implementation_sha256':sha(__file__),
            'dependency_sha256':{name:sha(Path(__file__).with_name(name))for name in ['pack_patch001_character.py','build_occluded_underlays.py','patch001_factory.py']},
            'unique_pixel_objects':len(objects),'hidden_pixels_preserved':True,
            'per_frame_fitting':False,'runtime_admitted':False}
    (args.output/'package.json').write_text(json.dumps(report,indent=2)+'\n')
    shutil.copyfile(__file__,args.output/'renderer-source.py')
    replay=args.output/'replay';replay.mkdir()
    for name in ['package_layered_hold.py','pack_patch001_character.py','build_occluded_underlays.py','patch001_factory.py']:
        shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'variants':len(variants),'unique_objects':len(objects),'atlas_pages':len(pages),'hidden_pixels_preserved':True}))


if __name__=='__main__':main()
