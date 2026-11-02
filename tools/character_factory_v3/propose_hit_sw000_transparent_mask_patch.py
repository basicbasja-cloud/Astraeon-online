"""Compose a same-frame bounded transparent donor using an unapproved blade mask."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates';BASE=P/'swordsman-hit-sw000-bounded-repair-20261102/draft.png';C=P/'swordsman-hit-sw000-close-transparent-20261102'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 src=Image.open(BASE).convert('RGBA');donor=Image.open(C/'raw.png').convert('RGBA');sm=Image.open(C/'source-blade-mask.png').convert('L');targets=json.loads((C/'source-targets.json').read_text())['weapon_targets_authoring_px']
 if src.size!=(768,768) or donor.size!=(1254,1254) or sm.size!=(1000,1000):raise ValueError('unexpected input size')
 patch=np.asarray(donor.resize((125,125),Image.Resampling.LANCZOS));m0=binary_dilation(np.asarray(sm.resize((125,125),Image.Resampling.NEAREST))>0,iterations=1);mask=np.zeros((768,768),bool);mask[355:480,330:455]=m0;a=np.asarray(src);full=np.zeros_like(a);full[355:480,330:455]=patch;b=a.copy();b[mask]=full[mask]
 if np.any(a[~mask]!=b[~mask]):raise ValueError('outside-mask change')
 removed=(a[:,:,3]>=240)&(b[:,:,3]<10);added=(a[:,:,3]<10)&(b[:,:,3]>=240);t=targets['tip'];rawtarget=((t[0]-330)*1254/125,(t[1]-355)*1254/125);manual=(806,404);error=math.dist(manual,rawtarget)*125/1254*240/768
 out.mkdir(parents=True);Image.fromarray(b).save(out/'candidate.png');Image.fromarray(mask.astype('uint8')*255).save(out/'mask.png');Image.fromarray(removed.astype('uint8')*255).save(out/'removed-opaque-mask.png');board=Image.new('RGB',(1200,800));d=ImageDraw.Draw(board)
 for row,img in enumerate((src,Image.fromarray(b))):
  for col,c in enumerate(('white','#777','#222')):
   bg=Image.new('RGBA',(768,768),c);bg.alpha_composite(img);board.paste(bg.crop((310,310,460,460)).resize((400,400),Image.Resampling.NEAREST).convert('RGB'),(col*400,row*400));d.text((col*400+3,row*400+3),'original' if row==0 else 'bounded donor / draft',fill='red')
 board.save(out/'comparison.png');proof={'status':'TRANSPARENT_MASK_PATCH_NOT_APPROVED','inputs_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (BASE,C/'raw.png',C/'source-blade-mask.png',C/'source-targets.json')},'script_sha256':sha(Path(__file__)),'mask_pixels':int(mask.sum()),'outside_mask_difference':0,'opaque_to_transparent_pixels':int(removed.sum()),'transparent_to_opaque_pixels':int(added.sum()),'manual_tip_raw_px':manual,'guide_tip_raw_px':rawtarget,'tip_error_runtime_px':error,'manual_uncertainty_raw_px':4,'limitations':['The 53 opaque-to-transparent pixels may include arm/body, not solely the former blade; inspect semantic ownership.', 'SAM blade and its dilation may include costume/glove; compare edges and seams frame by frame.', 'Manual donor tip and finger-derived guide proxy do not validate real socket, hand, anatomy or foot contacts.', 'One source master draft, one direction, no cutouts, variants, animation or gameplay.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
