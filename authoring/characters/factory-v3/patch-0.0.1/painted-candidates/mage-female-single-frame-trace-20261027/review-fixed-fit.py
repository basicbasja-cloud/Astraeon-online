"""One calibration for all single-frame studies; never per-pose body resizing."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from PIL import Image,ImageDraw

sys.path.insert(0,'tools/character_factory_v3')
from normalize_fixed_viewport_batch import normalize_batch
from register_planted_foot_masters import observed_sole, rigid_translation

BASE=Path('authoring/characters/factory-v3/patch-0.0.1')
PAINT=Path(__file__).parent
OUT=BASE/'review/mage-female-single-frame-trace-20261027'
GUIDE=BASE/'research/tall-guide-proportion-pilot-20261027/mage130-colored-high1536-capture'

def soles(im):
    candidates=observed_sole(im)[1]
    if len(candidates)!=2:
        raise ValueError('Both visible soles must be reviewed, no guessed foot association')
    return np.asarray(sorted([r['point']for r in candidates]))

def normalize(index):
    path=PAINT/f'raw{index:03d}.png'
    sequence=json.loads((PAINT/'sequence-reference-recipe.json').read_text())
    viewport=sequence['canonical_viewport768']if index in sequence['indices']else[224,224,576,576]
    return normalize_batch(Image.open(path),{'grid':[1,1],'source_size':[768,768],'viewport':viewport,'source_pose_indices':[index]})[0][0]

def guide(index):
    return Image.open(GUIDE/'SW'/f'{index:03d}.png').convert('RGBA').resize((768,768),Image.Resampling.LANCZOS)

def main():
    (OUT/'Master').mkdir(parents=True,exist_ok=True)
    (OUT/'Overlays').mkdir(exist_ok=True)
    reference=22
    paint0=normalize(reference);target=soles(guide(reference));observed=soles(paint0)
    scale=float((target[1,0]-target[0,0])/(observed[1,0]-observed[0,0]))
    translation=target.mean(axis=0)-scale*observed.mean(axis=0)
    if not .8<scale<1.2:
        raise ValueError('Unexpected global fit requires explicit review')
    records=[]
    indices=[i for i in range(24)if(PAINT/f'raw{i:03d}.png').exists()]
    contact=Image.new('RGBA',(384*6,384*((len(indices)+5)//6)),'#ddd')
    for slot,index in enumerate(indices):
        im=normalize(index)
        im=im.convert('RGBa').transform((768,768),Image.Transform.AFFINE,(1/scale,0,-float(translation[0])/scale,0,1/scale,-float(translation[1])/scale),Image.Resampling.BICUBIC).convert('RGBA')
        expected=soles(guide(index));before=soles(im)
        delta=np.rint(expected.mean(axis=0)-before.mean(axis=0)).astype(int)
        im=rigid_translation(im,delta);actual=soles(im)
        errors=np.linalg.norm(actual-expected,axis=1)
        im.save(OUT/'Master'/f'{index:03d}.png')
        overlay=guide(index)
        a=im.getchannel('A').point(lambda value:round(value*.6));faded=im.copy();faded.putalpha(a);overlay.alpha_composite(faded)
        overlay.save(OUT/'Overlays'/f'{index:03d}.png')
        contact.alpha_composite(im.crop((192,256,576,640)),((slot%6)*384,(slot//6)*384));ImageDraw.Draw(contact).text(((slot%6)*384+4,(slot//6)*384+5),f'{index}: study, NOT admitted',fill='black')
        records.append({'index':index,'raw_sha256':hashlib.sha256((PAINT/f'raw{index:03d}.png').read_bytes()).hexdigest(),'whole_frame_integer_translation':delta.tolist(),'source_raster_soles':expected.tolist(),'painted_raster_soles':actual.tolist(),'sole_errors_authoring_px':errors.tolist(),'calibration_pose_not_independent_validation':index==reference,'narrow_two_visible_sole_check_within3_authoring_px':bool(errors.max()<=3),'anatomy_grip_costume_continuity_approved':False})
    contact.convert('RGB').save(OUT/'key-contact.jpg',quality=98)
    (OUT/'receipt.json').write_text(json.dumps({'status':'SINGLE_FRAME_GUIDE_TRACE_STUDY_NOT_PRODUCTION','calibration_pose':reference,'shared_scale':scale,'shared_translation':translation.tolist(),'same_scale_all_poses':True,'per_frame_body_or_limb_warp':False,'calibration_note':'One provisional guide/body fit from the first available pose22; hold fixed for every later pose. Raster sole checks are not full anatomical acceptance.','frames':records,'full24_complete':False,'runtime_admitted':False},indent=2)+'\n')
    print(json.dumps({'shared_scale':scale,'translation':translation.tolist(),'frames':records}))

if __name__=='__main__':
    main()
