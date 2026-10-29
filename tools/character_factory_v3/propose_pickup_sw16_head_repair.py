"""Apply bounded donor repair to one SW16 head/neck master draft."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates'
INITIAL=P/'swordsman-pickup-sw16-single-20261029/generated.png'
DONOR=P/'swordsman-pickup-sw16-head-repair-20261029/donor-extra.png'
ROI=(720,590,920,800);FEATHER=12
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 source=Image.open(INITIAL).convert('RGB');donor=Image.open(DONOR).convert('RGB')
 if source.size!=(1254,1254) or donor.size!=source.size:raise ValueError('Unexpected input canvas')
 mask=Image.new('L',source.size);ImageDraw.Draw(mask).rectangle(ROI,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(FEATHER));m=np.array(mask);a=np.array(source);candidate=Image.composite(donor,source,mask);b=np.array(candidate)
 if np.any(a[m==0]!=b[m==0]):raise ValueError('Pixels outside repair mask changed')
 out.mkdir(parents=True);candidate.save(out/'candidate.png');mask.save(out/'repair-mask.png');board=Image.new('RGB',(1152,420),'white');draw=ImageDraw.Draw(board)
 for i,(title,im) in enumerate([('Before',source),('Donor',donor),('Bounded repair',candidate)]):board.paste(im.resize((384,384),Image.Resampling.LANCZOS),(384*i,36));draw.text((384*i+4,8),title,fill='black')
 board.save(out/'comparison.png');proof={'status':'BOUNDED_HEAD_REPAIR_DRAFT_NOT_APPROVED','roi_source_px':ROI,'feather_px':FEATHER,'initial_sha256':sha(INITIAL),'donor_sha256':sha(DONOR),'changed_pixels':int(np.any(a!=b,axis=2).sum()),'outside_mask_changed_pixels':0,'source_modified':False,'runtime_admitted':False,'limitations':['The mask can include scarf and shoulder pixels and does not prove anatomical continuity.','SAM head centroid is a diagnostic, not a landmark or production gate.','Independent generated frames, alpha and runtime remain unapproved.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
