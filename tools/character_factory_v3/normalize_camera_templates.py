"""Normalize separately drawn static camera templates before any motion reuse.

One common scale and recorded per-camera static offsets apply to source pose
zero. Native cameras stay fixed. This tool does not normalize animation frames.
"""
import argparse
import json
from pathlib import Path
import shutil

from PIL import Image,ImageDraw
import normalize_fixed_viewport_batch as viewport
from normalize_single_art_template import calibrate,sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['image','guide','recipe','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Choose a fresh static camera template output')
    recipe=json.loads(args.recipe.read_text());capture=json.loads((args.guide/'pilot-receipt.json').read_text())
    directions=recipe['directions'];index=recipe['source_pose_index']
    if len(directions)!=len(set(directions))or set(directions)-set(capture['views']):raise ValueError('Unknown or duplicate static cameras')
    if len(directions)!=recipe['grid'][0]*recipe['grid'][1]:raise ValueError('One static camera required per cell')
    cells={'grid':recipe['grid'],'source_size':[1536,1536],'viewport':recipe['viewport'],
           'source_pose_indices':list(range(len(directions)))}
    # Dense cell IDs above are extraction slots, never source motion indices.
    frames,diagnostic=viewport.normalize_batch(Image.open(args.image),cells)
    if diagnostic['production_blockers']:raise ValueError('Static camera template is clipped')
    records=[];inputs={str(p):sha(p)for p in [args.image,args.recipe,args.guide/'pilot-receipt.json']}
    args.output.mkdir(parents=True)
    for direction,frame in zip(directions,frames,strict=True):
        native=capture['views'][direction]['frames'][index]
        reference=args.guide/direction/f'{index:03d}.png'
        if sha(reference)!=native['image_sha256']:raise ValueError('Native camera reference changed')
        inputs[str(reference)]=sha(reference)
        image=calibrate(frame,recipe['common_art_scale'],recipe['static_offsets'][direction])
        folder=args.output/direction/'BodyCostume';folder.mkdir(parents=True)
        path=folder/'000.png';image.save(path)
        debug=Image.new('RGBA',image.size,'#aaa');debug.alpha_composite(image);draw=ImageDraw.Draw(debug)
        keys=['Head','Chest','Hips','UpperArm.L','Forearm.L','Hand.L','UpperArm.R','Forearm.R','Hand.R','Foot.L','Foot.R']
        for key in keys:
            x,y=native['landmarks'][key];draw.ellipse((x-3,y-3,x+3,y+3),fill='#00ffff');draw.text((x+5,y),key,fill='#00ffff')
        debug.save(args.output/direction/'native-joint-overlay.png')
        records.append({'direction':direction,'source_pose_index':index,'source_action':native['source_action'],'source_frame':native['source_frame'],
                        'body_sha256':sha(path),'static_offset':recipe['static_offsets'][direction],
                        'native_camera':capture['views'][direction]['camera']})
    (args.output/'receipt.json').write_text(json.dumps({'status':'STATIC_BODY_CAMERA_TEMPLATES_REQUIRE_ANATOMICAL_REGISTRATION',
          'input_sha256':inputs,'implementation_sha256':sha(__file__),'common_art_scale':recipe['common_art_scale'],
          'per_frame_fitting':False,'camera_changed':False,'frames':records,'source_pose_alignment_approved':False,
          'runtime_admitted':False},indent=2)+'\n')
    replay=args.output/'replay';replay.mkdir()
    for name in ['normalize_camera_templates.py','normalize_fixed_viewport_batch.py','normalize_single_art_template.py','derive_bounded_hold_parts.py']:
        shutil.copyfile(Path(__file__).with_name(name),replay/name)


if __name__=='__main__':main()
