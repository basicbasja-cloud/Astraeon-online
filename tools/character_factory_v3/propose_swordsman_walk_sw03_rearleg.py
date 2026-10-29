"""Bounded follow-up repaint on an unapproved full-body SW03 master."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-walk-sw-rearleg-repair-20261029/candidate.png'
DONOR=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw03-rearleg-repair-20261029/donor.png'

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 with Image.open(SOURCE) as im:
  if im.size!=(1774,887):raise ValueError('unexpected source geometry')
  original=im.convert('RGB').crop((887,0,1774,887))
 with Image.open(DONOR) as im:
  if im.size!=(1254,1254):raise ValueError('unexpected donor geometry')
  donor=im.convert('RGB').resize((887,887),Image.Resampling.LANCZOS)
 mask=Image.new('L',(887,887));ImageDraw.Draw(mask).rounded_rectangle((180,480,465,730),radius=16,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(5));result=Image.composite(donor,original,mask)
 a=np.asarray(original);b=np.asarray(result);m=np.asarray(mask);changed=np.any(a!=b,axis=2);outside=int((changed&(m==0)).sum())
 if outside:raise ValueError('outside-mask changes')
 out.mkdir(parents=True);original.save(out/'source.png');result.save(out/'candidate.png');mask.save(out/'mask.png')
 proof={'status':'SW03_BOUNDED_MASTER_REPAIR_NOT_APPROVED','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'donor_sha256':hashlib.sha256(DONOR.read_bytes()).hexdigest(),'mask_rectangle':[180,480,465,730],'blur_radius':5,'changed_pixels':int(changed.sum()),'outside_mask_changed_pixels':outside,
        'limitations':['The mask includes thigh/costume and may create seams.', 'Bone origin is not a confirmed ankle or contact; only frame 03 was corrected.', 'Head drift, motion, cutouts, variants and runtime remain unapproved.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
