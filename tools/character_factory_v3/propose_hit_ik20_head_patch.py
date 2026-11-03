"""Propose bounded head-pixel edits for Hit SW frames 05 and 06, unapproved."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates';SRC=P/'swordsman-hit-sw-floor-ik20-20261103/paint.png';DONOR=P/'swordsman-hit-sw-floor-ik20-head-edit-20261103/donor.png';BOXES=((75,310,155,373),(356,310,436,373))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 base=Image.open(SRC).convert('RGB');donor=Image.open(DONOR).convert('RGB')
 if base.size!=donor.size or base.size!=(1403,1121):raise ValueError('unexpected source dimensions')
 mask=Image.new('L',base.size);draw=ImageDraw.Draw(mask)
 for x0,y0,x1,y1 in BOXES:draw.rounded_rectangle((x0+3,y0+3,x1-3,y1-3),radius=7,fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(1.5));allowed=np.zeros((base.height,base.width),bool)
 for x0,y0,x1,y1 in BOXES:allowed[y0:y1+1,x0:x1+1]=True
 marr=np.array(mask);marr[~allowed]=0;mask=Image.fromarray(marr)
 candidate=Image.composite(donor,base,mask);a=np.array(base);b=np.array(candidate);changed=np.any(a!=b,axis=2)
 if np.any(changed & ~allowed):raise ValueError('pixel change outside allowed boxes')
 out.mkdir(parents=True);candidate.save(out/'paint.png');mask.save(out/'mask.png')
 (out/'receipt.json').write_text(json.dumps({'status':'BOUNDED_MASTER_DRAFT_NOT_APPROVED','boxes_xyxy_inclusive':BOXES,'changed_pixels':int(changed.sum()),'changed_outside_boxes':int((changed & ~allowed).sum()),'source_sha256':sha(SRC),'donor_sha256':sha(DONOR),'script_sha256':sha(Path(__file__)),'limitations':['Boxes include part of hair, neck and scarf; seam and ownership need human review.','Image model drift may misregister donor within boxes.','Other poses, limb anatomy, contacts, grip, game transitions and other views are not approved.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
