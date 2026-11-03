"""Draft same-frame scarf underpaint behind an opaque weapon, for inspection only."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import propose_nw005_scarf_ownership as scarf
import propose_nw005_hidden_hair as hair

def build(out, scarf_dir):
    if out.exists() or out.is_symlink():
        raise ValueError('fresh output required')
    parts = {}
    for role in scarf.ORDER:
        path = scarf_dir / (role + '.png') if role in ('BodyCostume','Weapon') else scarf.H if role == 'HeadHair' else scarf.SRC / role / '005.png'
        parts[role] = np.array(Image.open(path).convert('RGBA'))
    donor = np.array(Image.open(hair.DONOR).convert('RGB').resize((80,80),Image.Resampling.LANCZOS))
    full = np.full((512,512,3),255,np.uint8)
    full[170:250,220:300] = donor
    yy,xx=np.indices((512,512))
    r,g,b=full.astype(int).transpose(2,0,1)
    mask=(xx>=235)&(xx<277)&(yy>=220)&(yy<242)&(parts['Weapon'][:,:,3]==255)&(parts['BodyCostume'][:,:,3]==0)&(parts['HeadHair'][:,:,3]==0)&(full.min(axis=2)<220)
    parts['BodyCostume'][mask,:3]=full[mask]
    parts['BodyCostume'][mask,3]=255
    canvas=Image.new('RGBA',(512,512))
    for role in scarf.ORDER: canvas.alpha_composite(Image.fromarray(parts[role]))
    original=np.array(Image.open(scarf.SRC/'Master/005.png').convert('RGBA'))
    if not np.array_equal(original,np.asarray(canvas)): raise ValueError('master mismatch')
    out.mkdir(parents=True)
    Image.fromarray(parts['BodyCostume']).save(out/'BodyCostume.png')
    Image.fromarray((mask*255).astype('uint8')).save(out/'underpaint-mask.png')
    canvas.save(out/'recomposed.png')
    board=Image.new('RGB',(800,430),'#777'); d=ImageDraw.Draw(board)
    for i,(label,bd) in enumerate((('before',np.array(Image.open(scarf_dir/'BodyCostume.png').convert('RGBA'))),('with hidden scarf',parts['BodyCostume']))):
        layer=Image.new('RGBA',(512,512));layer.alpha_composite(Image.fromarray(bd));layer.alpha_composite(Image.fromarray(parts['HeadHair']));layer.alpha_composite(Image.fromarray(parts['WeaponHandOccluder']))
        bg=Image.new('RGBA',(512,512),'#777');bg.alpha_composite(layer);board.paste(bg.crop((220,170,300,250)).resize((400,400),Image.Resampling.NEAREST).convert('RGB'),(i*400,25));d.text((i*400+3,3),label,fill='white')
    board.save(out/'without-weapon-comparison.png')
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    receipt={'status':'SINGLE_FRAME_UNAPPROVED_DRAFT','underpaint_pixels':int(mask.sum()),'master_sha256':digest(scarf.SRC/'Master/005.png'),'donor_sha256':digest(hair.DONOR),'body_input_sha256':digest(scarf_dir/'BodyCostume.png'),'weapon_sha256':digest(scarf_dir/'Weapon.png'),'script_sha256':digest(Path(__file__)),'rgba_mismatch':0,'limitations':['Donor is generated and not a recovered hidden surface; scarf boundary and continuity require visual review. The nonwhite filter can put hair pixels into BodyCostume.','Semi-transparent blade edges and uncovered areas may still have holes.','One frame only; no alternate weapon, animation or gameplay validated.']}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--scarf-dir',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output,a.scarf_dir)))
