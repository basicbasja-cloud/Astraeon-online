"""Apply a bounded donor repaint to two unapproved complete walk masters."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates'
SOURCE=P/'swordsman-walk-sw-adjacent-pairs-20261029/paint-02-03.png'
DONOR=P/'swordsman-walk-sw-rearleg-repair-20261029/donor.png'

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 with Image.open(SOURCE) as im:source=im.convert('RGB')
 with Image.open(DONOR) as im:donor=im.convert('RGB')
 if source.size!=(1774,887) or donor.size!=source.size:raise ValueError('pair canvas changed')
 mask=Image.new('L',source.size);draw=ImageDraw.Draw(mask)
 for i in range(2):draw.rounded_rectangle((i*887+180,480,i*887+465,730),radius=16,fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(5));result=Image.composite(donor,source,mask)
 a=np.asarray(source);b=np.asarray(result);m=np.asarray(mask);changed=np.any(a!=b,axis=2);outside=int((changed&(m==0)).sum())
 if outside:raise ValueError('outside-mask changes')
 out.mkdir(parents=True);source.save(out/'source.png');result.save(out/'candidate.png');mask.save(out/'mask.png')
 receipt={'status':'TWO_FRAME_BOUNDED_MASTER_REPAIR_NOT_APPROVED','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'donor_sha256':hashlib.sha256(DONOR.read_bytes()).hexdigest(),'mask_rounded_rectangles':[[180,480,465,730],[1067,480,1352,730]],'blur_radius':5,'changed_pixels':int(changed.sum()),'outside_mask_changed_pixels':outside,
          'limitations':['Mask includes part of thigh/costume and cannot certify anatomy or mask seams.', 'Guide bone origin is not a verified painted ankle or sole contact.', 'Head drift, other walk frames, alpha, cutouts, gameplay and runtime remain unapproved.']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
