"""Bounded complete-master NW003 sword removal study, not cutout acceptance."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import propose_swordsman_nw008_blade_ownership as base
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw003-underpaint-20261030/raw.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 parts={}
 for role in base.ORDER:
  with Image.open(base.SOURCE/role/'003.png') as im:parts[role]=im.convert('RGBA')
 original=Image.new('RGBA',(512,512))
 for role in ('BodyCostume','HeadHair','WeaponHandOccluder'):original.alpha_composite(parts[role])
 with Image.open(RAW) as im:donor=im.convert('RGB').resize((170,170),Image.Resampling.LANCZOS)
 rgb=np.asarray(donor).astype(float);minimum=np.min(rgb,axis=2); alpha=np.where(minimum < 220,255,np.clip((255-minimum)*255/35,0,255));denom=np.maximum(alpha,1)[:,:,None];colour=np.clip((rgb-(255-alpha[:,:,None]))*255/denom,0,255)
 patch=np.dstack((np.rint(colour).astype('uint8'),np.rint(alpha).astype('uint8')));patch[alpha<3]=0
 mask=Image.new('L',(512,512));d=ImageDraw.Draw(mask);d.line([(215,247),(317,184)],fill=255,width=18);d.ellipse((205,237,225,257),fill=255);mask=Image.fromarray(np.maximum(np.asarray(mask),np.asarray(parts['Weapon'].getchannel('A'))).astype('uint8')).filter(ImageFilter.MaxFilter(3))
 # Preserve every source pixel outside the explicit replacement mask.
 raw=np.asarray(original).copy();m=np.asarray(mask)>0;candidate=raw.copy();full=np.zeros_like(raw);full[130:300,180:350]=patch
 if np.any(m & ~((np.indices(m.shape)[1]>=180)&(np.indices(m.shape)[1]<350)&(np.indices(m.shape)[0]>=130)&(np.indices(m.shape)[0]<300))):raise ValueError('mask outside donor crop')
 candidate[m]=full[m]
 if np.any(candidate[~m]!=raw[~m]):raise ValueError('changed outside mask')
 out.mkdir(parents=True);Image.fromarray(candidate).save(out/'complete-master-no-weapon.png');mask.save(out/'mask.png')
 board=Image.new('RGB',(1200,800));draw=ImageDraw.Draw(board)
 for row,arr in enumerate((raw,candidate)):
  for col,c in enumerate(('white','#777777','#222222')):
   bg=Image.new('RGBA',(512,512),c);bg.alpha_composite(Image.fromarray(arr));z=bg.crop((180,130,350,300)).resize((400,400),Image.Resampling.LANCZOS);board.paste(z.convert('RGB'),(col*400,row*400));draw.text((col*400+3,row*400+3),'proposal' if row else 'original without weapon',fill='red')
 board.save(out/'comparison.png')
 proof={'status':'BOUNDED_COMPLETE_MASTER_UNDERPAINT_NOT_APPROVED','input_hashes':{k:sha(base.SOURCE/k/'003.png') for k in ('BodyCostume','HeadHair','Weapon','WeaponHandOccluder')},'donor_sha256':sha(RAW),'script_sha256':sha(Path(__file__)),'changed_mask_pixels':int(m.sum()),'outside_mask_exact':True,'limitations':['White-background alpha uses a heuristic and may leave halos or remove pale details.', 'The generated anatomy, garment continuity and mask seams require human visual review.', 'No clean modular slots, alternative weapon, remaining frames or runtime approval.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
