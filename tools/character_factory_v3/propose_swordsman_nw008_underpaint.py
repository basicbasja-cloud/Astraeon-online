"""Bounded, provisional NW008 blade-free background and scarf underpainting."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import propose_swordsman_nw008_blade_ownership as own

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw008-underpaint-20261030/raw.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 with Image.open(RAW) as im: donor=im.convert('RGB').resize((120,120),Image.Resampling.LANCZOS)
 parts={}
 for role in own.ORDER:
  with Image.open(own.SOURCE/role/'008.png') as im:parts[role]=im.convert('RGBA')
 source_body=np.asarray(parts['BodyCostume']).copy(); body=source_body.copy()
 # Approximate matte against the white generation background; bounded to the exposed blade and seam.
 rect=(275,225,283,245); x0,y0,x1,y1=rect; rgb=np.asarray(donor)[y0-180:y1-180,x0-210:x1-210].astype(float)
 alpha=255-np.min(rgb,axis=2); denom=np.maximum(alpha,1)[:,:,None];color=np.clip((rgb-(255-alpha[:,:,None]))*255/denom,0,255)
 patch=np.dstack((np.rint(color).astype('uint8'),np.rint(alpha).astype('uint8')));patch[alpha<3]=0
 body[y0:y1,x0:x1]=patch
 mask=np.zeros((512,512),bool);mask[y0:y1,x0:x1]=True
 if np.any(body[~mask]!=source_body[~mask]):raise ValueError('outside region changed')
 parts['BodyCostume']=Image.fromarray(body,'RGBA')
 def assemble(bodypart):
  result=Image.new('RGBA',(512,512))
  for role in ('BodyCostume','HeadHair','WeaponHandOccluder'):
   result.alpha_composite(bodypart if role=='BodyCostume' else parts[role])
  return result
 original=assemble(Image.fromarray(source_body,'RGBA')); candidate=assemble(parts['BodyCostume'])
 out.mkdir(parents=True);parts['BodyCostume'].save(out/'BodyCostume-underpaint.png');candidate.save(out/'without-weapon.png');Image.fromarray(mask.astype('uint8')*255).save(out/'bounded-mask.png')
 board=Image.new('RGB',(1536,1024));draw=ImageDraw.Draw(board)
 for y,(label,img) in enumerate((('existing body without Weapon slot',original),('provisional underpaint; no weapon',candidate))):
  for x,color in enumerate(('white','#777777','#222222')):
   bg=Image.new('RGBA',(512,512),color);bg.alpha_composite(img);board.paste(bg.convert('RGB'),(x*512,y*512));draw.text((x*512+5,y*512+5),label,fill='red')
 board.save(out/'background-comparison.png')
 result={'status':'PROVISIONAL_PARTIAL_UNDERPAINT_NOT_APPROVED','source_sha256':sha(own.SOURCE/'BodyCostume/008.png'),'donor_sha256':sha(RAW),'implementation_sha256':sha(Path(__file__)),'rect_xyxy':rect,'outside_region_exact':True,'limitations':['Approximate white-background matte is inferred, not ground-truth alpha; edge contamination possible.', 'The rectangle covers only the exposed blade and scarf intersection, not all hidden surfaces or weapon ownership.', 'No complete weapon swap, animated sequence, or gameplay validation.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
