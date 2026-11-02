"""Bound a generated whole-frame retouch to an explicit review-only weapon mask.

This preserves the same frame outside the mask; it does not repair geometry
inside it or approve the original draft's anatomy/contact/temporal consistency.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw
from review_swordsman_walk_locked_guides import ROOT,flat,controls,INSPECT

ORIGINAL=ROOT/'docs/character-factory/review/swordsman-walk-source-controls-20261102/key-authoring'
GUIDE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-guide-sealed-20261102/manifest.json'
POLYGON=((342,482),(342,451),(449,382),(470,385),(471,414),(380,471),(362,487))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output):
    if output.exists()or output.is_symlink():raise ValueError('Choose fresh reference output')
    manifest=json.loads(GUIDE.read_text());output.mkdir(parents=True)
    for index in (4,8,12):
        with Image.open(ORIGINAL/f'{index:03}.png')as image:
            original=image.convert('RGBA').crop((224,288,544,608)).resize((1280,1280),Image.Resampling.LANCZOS)
        original.save(output/f'{index:03}-original.png');target=original.copy();draw=ImageDraw.Draw(target);points=[]
        for name in ('grip','tip'):
            sx,sy=manifest['views']['SW']['frames'][index]['weapon_guide'][name]
            x,y=(sx/2-224)*4,(sy/2-288)*4;points.append((x,y))
            draw.ellipse((x-12,y-12,x+12,y+12),outline='#ff008a',width=4)
        draw.line(points,fill='#ff008a',width=3);target.save(output/f'{index:03}-target.png')
    receipt={'status':'REFERENCE_CANVASES_ONLY','source_crop_authoring':[224,288,544,608],
             'canvas':[1280,1280],'source_manifest_sha256':sha(GUIDE),
             'implementation_sha256':sha(Path(__file__)),
             'source_master_sha256':{str(i):sha(ORIGINAL/f'{i:03}.png')for i in (4,8,12)},
             'images_sha256':{p.name:sha(p)for p in sorted(output.glob('*.png'))}}
    (output/'reference-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def build(raw,output):
    if output.exists()or output.is_symlink():raise ValueError('Choose fresh proposal output')
    with Image.open(ORIGINAL/'004.png')as image:original=image.convert('RGBA')
    with Image.open(raw)as image:
        if image.mode!='RGBA'or image.size!=(1254,1254):raise ValueError('Unexpected generated full-frame crop')
        tile=image.convert('RGBa').resize((320,320),Image.Resampling.BICUBIC).convert('RGBA')
    generated=Image.new('RGBA',(768,768));generated.paste(tile,(224,288))
    stencil=Image.new('L',(768,768));ImageDraw.Draw(stencil).polygon(POLYGON,fill=255)
    mask=np.asarray(stencil)>0;before=np.array(original);candidate=before.copy();candidate[mask]=np.asarray(generated)[mask]
    changed=np.any(candidate!=before,axis=2)
    if np.any(changed&~mask):raise ValueError('Protected pixels changed')
    candidate=Image.fromarray(candidate);output.mkdir(parents=True)
    candidate.save(output/'master-candidate.png');stencil.save(output/'review-mask.png')
    board=Image.new('RGB',(1584,1000),'#cccccc');draw=ImageDraw.Draw(board)
    for row,image in enumerate((original,candidate)):
        for col,color in enumerate(('white','#777777','#222222')):
            board.paste(flat(image,color).crop((304,352,480,512)).resize((528,480),Image.Resampling.NEAREST),(col*528,row*500+20))
            draw.text((col*528+4,row*500+4),'same-frame original draft'if row==0 else'bounded retouch - NOT APPROVED',fill='red')
    board.save(output/'three-background-comparison.png')
    record=json.loads(GUIDE.read_text())['views']['SW']['frames'][4]
    panel=Image.new('RGB',(1248,448),'#eeeeee');draw=ImageDraw.Draw(panel)
    for col,(image,title)in enumerate(((flat(original),'ORIGINAL DRAFT'),(flat(candidate),'BOUNDED RETOUCH'),(controls(flat(candidate),record),'SOURCE CONTROLS / NOT APPROVED'))):
        panel.paste(image.crop(INSPECT),(col*416,32));draw.text((col*416+4,8),title,fill='black')
    panel.save(output/'source-control-comparison.png')
    observed_raw=[915,454];painted=[224+observed_raw[0]*320/1254,288+observed_raw[1]*320/1254]
    target=[p/2 for p in record['weapon_guide']['tip']]
    error=float(np.linalg.norm(np.array(painted)-np.array(target)))*.3125
    receipt={'status':'BOUNDED_MASTER_RETOUCH_NOT_APPROVED','index':4,'direction':'SW',
             'source_master_sha256':sha(ORIGINAL/'004.png'),'raw_generation_sha256':sha(raw),
             'guide_manifest_sha256':sha(GUIDE),'implementation_sha256':sha(Path(__file__)),
             'polygon_authoring_px':POLYGON,'mask_pixels':int(mask.sum()),'changed_pixels':int(changed.sum()),
             'changed_outside_mask':0,'whole_frame_crop_authoring':[224,288,544,608],
             'whole_frame_crop_resampled_uniformly':True,'per_frame_bbox_fit':False,
             'observed_visible_core_tip_raw_estimate':observed_raw,'tip_annotation_uncertainty_raw_px':3,
             'painted_tip_authoring_estimate':painted,'source_tip_authoring':target,
             'endpoint_distance_runtime_px_estimate':error,
             'source_original_overwritten':False,'source_pose_or_camera_changed':False,
             'new_cutouts_or_runtime_admission':False,
             'limitations':['The generated blade still misses the requested endpoint; this is not a geometry pass.',
                            'The explicit mask is a conservative retouch boundary, not certified semantic weapon ownership.',
                            'Hand/wrist, cloth seams, hidden surfaces, all intermediate poses and contact remain unapproved.',
                            'Preserving the same frame\'s legs does not validate the draft\'s foot motion or freeze/copy a leg from another frame.',
                            'Frames8 and12 did not receive generated outputs because the service rejected those two requests.']}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--raw',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.prepare:result=prepare(args.output)
    elif args.raw:result=build(args.raw,args.output)
    else:parser.error('--raw is required unless --prepare is selected')
    print(json.dumps({'status':result['status'],'outside_changes':result.get('changed_outside_mask')}))
