"""Bounded whole-master far-arm donor experiment; not an approved edit."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_propagation
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates';BASE=P/'swordsman-hit-sw000-bounded-repair-20261102/draft.png';DONOR=P/'swordsman-hit-sw000-arm-transparent-20261103/raw.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 src=Image.open(BASE).convert('RGBA');im=Image.open(DONOR).convert('RGBA')
 if src.size!=(768,768) or im.size!=(1254,1254):raise ValueError('unexpected size')
 donor=np.asarray(im.resize((320,320),Image.Resampling.LANCZOS));full=np.zeros((768,768,4),dtype='uint8');full[260:580,224:544]=donor;a=np.asarray(src);b=a.copy();y,x=np.indices(a.shape[:2]);mask=(x>=400)&(x<470)&(y>=340)&(y<445);b[mask]=full[mask]
 if np.any(a[~mask]!=b[~mask]):raise ValueError('outside-mask difference')
 out.mkdir(parents=True);Image.fromarray(b).save(out/'candidate.png');Image.fromarray((mask*255).astype('uint8')).save(out/'mask.png');board=Image.new('RGB',(1200,800));d=ImageDraw.Draw(board)
 for row,arr in enumerate((a,b)):
  for col,c in enumerate(('white','#777','#222')):
   bg=Image.new('RGBA',(768,768),c);bg.alpha_composite(Image.fromarray(arr));board.paste(bg.crop((310,310,470,470)).resize((400,400),Image.Resampling.LANCZOS).convert('RGB'),(col*400,row*400));d.text((col*400+3,row*400+3),'original' if row==0 else 'bounded whole-master draft',fill='red')
 board.save(out/'comparison.png');proof={'status':'TRANSPARENT_BOUNDED_FAR_ARM_NOT_APPROVED','source_sha256':sha(BASE),'donor_sha256':sha(DONOR),'script_sha256':sha(Path(__file__)),'mask_pixels':int(mask.sum()),'outside_mask_difference':0,'limitations':['Generated background removal redrew details and its alpha/edge must be reviewed.', 'Donor/source seam, far-arm anatomy and corresponding hand landmark remain unapproved.', 'One frame only; sword, feet, animation, cutouts, variants and game remain unapproved.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
