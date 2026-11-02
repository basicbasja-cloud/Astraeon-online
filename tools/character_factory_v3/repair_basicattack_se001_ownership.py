"""Move the reviewed SE001 hair fragment out of Weapon without repainting art.

Only one retained frame is corrected. Grip/hidden-surface, source-pose and full
sequence gates remain separate. Originals are immutable inputs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/SE'
POLYGON=[(187,156),(190,156),(227,175),(228,178),(228,179),(227,180),(225,179),(187,160)]
ROLES=('Master','BodyCostume','HeadHair','Weapon','WeaponHandOccluder')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def compose(parts,roles):
    canvas=Image.new('RGBA',(512,512))
    for role in roles:canvas.alpha_composite(Image.fromarray(parts[role]))
    return canvas


def repair(output):
    if output.exists()or output.is_symlink():raise ValueError('Choose fresh output')
    paths={r:SOURCE/r/'001.png'for r in ROLES};pins={str(p.relative_to(ROOT)):sha(p)for p in paths.values()}
    original={r:np.asarray(Image.open(p).convert('RGBA')).copy()for r,p in paths.items()}
    changed={r:array.copy()for r,array in original.items()}
    mask=Image.new('1',(512,512));ImageDraw.Draw(mask).polygon(POLYGON,fill=1)
    # Conservative visible-metal region, checked against enlarged native artwork.
    pixels=original['Weapon'].astype(np.int16)
    metal=np.asarray(mask,dtype=bool)&(pixels[:,:,2]>=pixels[:,:,0]-1)
    selected=(original['Weapon'][:,:,3]>0)&~metal
    if np.any(selected&(original['HeadHair'][:,:,3]>0)):raise ValueError('Destination overlaps existing head pixels')
    changed['HeadHair'][selected]=original['Weapon'][selected];changed['Weapon'][selected]=0
    core=('BodyCostume','HeadHair','Weapon')
    if not np.array_equal(np.asarray(compose(changed,core)),original['Master']):raise ValueError('Core does not reproduce full master')
    if not np.array_equal(np.asarray(compose(changed,(*core,'WeaponHandOccluder'))),original['Master']):raise ValueError('Occluder changes original art')
    output.mkdir(parents=True)
    for role,array in changed.items():Image.fromarray(array).save(output/f'{role}.png')
    Image.fromarray(selected.astype('uint8')*255).save(output/'transferred-hair-mask.png')
    panels=[]
    for background in ('#eeeeee','#303038'):
        board=Image.new('RGB',(1024,544),background);draw=ImageDraw.Draw(board)
        for n,parts in enumerate((original,changed)):
            visible=compose(parts,('Weapon',));bg=Image.new('RGBA',(512,512),background);bg.alpha_composite(visible);board.paste(bg.convert('RGB'),(n*512,32));draw.text((n*512+8,8),['BEFORE WEAPON','AFTER WEAPON'][n],fill='#d00000')
        panels.append(board)
    panels[0].save(output/'weapon-light.png');panels[1].save(output/'weapon-dark.png')
    crop=(176,136,288,208);board=Image.new('RGB',(896,576),'white')
    for n,parts in enumerate((original,changed)):
        bg=Image.new('RGBA',(112,72),'#404048');bg.alpha_composite(compose(parts,('Weapon',)).crop(crop));board.paste(bg.resize((448,288),Image.Resampling.NEAREST).convert('RGB'),(n*448,0))
        bg=Image.new('RGBA',(112,72),'#404048');bg.alpha_composite(compose(parts,('HeadHair',)).crop(crop));board.paste(bg.resize((448,288),Image.Resampling.NEAREST).convert('RGB'),(n*448,288))
    board.save(output/'native-boundary-review.png')
    for p,digest in pins.items():assert sha(ROOT/p)==digest
    result={'status':'ONE_FRAME_VISIBLE_OWNERSHIP_REPAIR_NOT_ACTION_APPROVAL','direction':'SE','index':1,
        'moved_visible_pixels_weapon_to_headhair':int(selected.sum()),'weapon_pixels_before':int((original['Weapon'][:,:,3]>0).sum()),
        'weapon_pixels_after':int((changed['Weapon'][:,:,3]>0).sum()),'visible_metal_polygon_native512':POLYGON,
        'blue_vs_red_threshold':-1,'core_rgba_recomposition_exact':True,'with_existing_occluder_rgba_exact':True,
        'master_body_and_occluder_rgba_unchanged':True,'source_or_pose_modified':False,'headhair_rgba_only_received_same_frame_source_pixels':True,
        'hidden_surfaces_authored':False,'sole_contact_approved':False,'full_sequence_approved':False,'runtime_admitted':False,
        'source_sha256':pins,'implementation_sha256':sha(Path(__file__)),
        'limitations':['Visible blade/hair boundary includes mixed edge pixels and needs final sequence review.',
                       'Only this one SE frame is repaired; other frames retain known ownership defects.',
                       'No held-sword volume, actual grip, occlusion swap, hidden underpaint or gameplay acceptance.']}
    (output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();print(json.dumps(repair(args.output)))
