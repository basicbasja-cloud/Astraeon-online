"""Evaluate a manual blade polygon against the preserved NW003 master."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import propose_swordsman_nw008_blade_ownership as base
ROOT=Path(__file__).resolve().parents[2]
UNDER=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-underpaint-20261030/complete-master-no-weapon.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 masterpath=base.SOURCE/'Master/003.png'
 with Image.open(masterpath) as im:master=im.convert('RGBA')
 mask=Image.new('L',(512,512));ImageDraw.Draw(mask).polygon([(225,234),(303,180),(306,179),(308,180),(306,185),(231,240)],fill=255)
 blade=Image.new('RGBA',(512,512));blade.paste(master,(0,0),mask)
 with Image.open(UNDER) as im:under=im.convert('RGBA')
 proposal=under.copy();proposal.alpha_composite(blade)
 for role in ('Weapon','WeaponHandOccluder'):
  with Image.open(base.SOURCE/role/'003.png') as im:proposal.alpha_composite(im.convert('RGBA'))
 a=np.asarray(master);b=np.asarray(proposal);different=np.any(a!=b,axis=2);alpha=a[:,:,3]!=b[:,:,3]
 out.mkdir(parents=True);blade.save(out/'blade-polygon.png');mask.save(out/'blade-polygon-mask.png');proposal.save(out/'restored.png');Image.fromarray(different.astype('uint8')*255,'L').save(out/'rgba-difference-mask.png')
 board=Image.new('RGB',(1200,800));draw=ImageDraw.Draw(board)
 for row,im in enumerate((master,proposal)):
  for col,color in enumerate(('white','#777777','#222222')):
   bg=Image.new('RGBA',(512,512),color);bg.alpha_composite(im);board.paste(bg.crop((180,130,350,300)).resize((400,400),Image.Resampling.LANCZOS).convert('RGB'),(400*col,400*row));draw.text((400*col+3,400*row+3),'preserved master' if row==0 else 'experimental recovery / not exact',fill='red')
 board.save(out/'comparison.png')
 proof={'status':'MANUAL_BLADE_RECOVERY_NOT_APPROVED','master_sha256':sha(masterpath),'underpaint_sha256':sha(UNDER),'script_sha256':sha(Path(__file__)),'rgba_difference_pixels':int(different.sum()),'alpha_difference_pixels':int(alpha.sum()),'limitations':['Polygon contains some scarf or skin edge pixels and lacks a separate full hilt.', 'The legacy Weapon layer and hand occluder are still used, with known semantic contamination.', 'Exact master recomposition, clean swaps and other frames remain unresolved.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
