"""Bounded generated-donor repair of a SW00 sword and free-hand draft.

Keeps every source pixel outside one fixed feathered region. This is a draft,
not a guide match, cutout, temporal continuity or runtime approval.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw00-repair-20261029'
ROI=(430,530,910,730);FEATHER=12

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out,donor_path=BASE/'donor.png'):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 paths=[BASE/'initial.png',donor_path];initial,donor=[Image.open(p).convert('RGB') for p in paths]
 if initial.size!=(1254,1254) or donor.size!=initial.size:raise ValueError('Unexpected donor canvas')
 mask=Image.new('L',initial.size);ImageDraw.Draw(mask).rectangle(ROI,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(FEATHER));a=np.array(initial);b=np.array(mask);repaired=Image.composite(donor,initial,mask);r=np.array(repaired)
 if np.any(r[b==0]!=a[b==0]):raise ValueError('Pixels outside the bounded mask changed')
 out.mkdir(parents=True);repaired.save(out/'candidate.png');mask.save(out/'repair-mask.png');panel=Image.new('RGB',(1152,420),'white');draw=ImageDraw.Draw(panel);guide=Image.open(BASE/'guide.png').convert('RGB')
 for i,(title,img) in enumerate([('Guide',guide),('Initial',initial.resize((384,384),Image.Resampling.LANCZOS)),('Bounded donor repair',repaired.resize((384,384),Image.Resampling.LANCZOS))]):panel.paste(img,(i*384,36));draw.text((i*384+4,8),title,fill='black')
 panel.save(out/'comparison.png');proof={'status':'BOUNDED_GRIP_REPAIR_DRAFT_NOT_APPROVED','roi_source_px':ROI,'feather_px':FEATHER,'source_sha256':{p.name:sha(p) for p in paths},'changed_pixels':int(np.any(a!=r,axis=2).sum()),'outside_mask_changed_pixels':0,'source_modified':False,'runtime_admitted':False,'limitations':['Sword trajectory and hand separation need exact guide and 3D grip review.','Feathered patch may contain donor changes inside the region.','No cutouts, motion continuity or other frames are established.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--donor',type=Path,default=BASE/'donor.png');a=p.parse_args();print(json.dumps(build(a.output,a.donor)))
