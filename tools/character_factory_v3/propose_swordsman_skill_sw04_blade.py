"""Propose a bounded blade paint correction to a non-approved SW04 key pose."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates'
SOURCE=P/'swordsman-skill-sw-keyposes-20261029/generated.png'
DONOR=P/'swordsman-skill-sw04-blade-repair-20261029/donor.png'

def build(out):
 if out.exists() or out.is_symlink(): raise ValueError('choose fresh output')
 with Image.open(SOURCE) as im:
  original=im.convert('RGB').crop((im.width//4,0,im.width//2,im.height//2))
 with Image.open(DONOR) as im:
  donor=im.convert('RGB').resize(original.size,Image.Resampling.LANCZOS)
 # The donor is registered only for a bounded drawing proposal, not the body.
 shifted=Image.new('RGB', original.size, 'white');shifted.paste(donor,(-3,2))
 mask=Image.new('L',original.size);ImageDraw.Draw(mask).rectangle((150,0,209,104),fill=255);mask=mask.filter(ImageFilter.GaussianBlur(3))
 result=Image.composite(shifted,original,mask)
 a=np.asarray(original);b=np.asarray(result);m=np.asarray(mask)
 changed=np.any(a!=b,axis=2)
 outside=int(np.count_nonzero(changed & (m==0)))
 if outside: raise RuntimeError('modified outside mask')
 out.mkdir(parents=True);original.save(out/'initial.png');result.save(out/'candidate.png');mask.save(out/'mask.png')
 panel=Image.new('RGB',(original.width*2,original.height+25),'white');panel.paste(original,(0,25));panel.paste(result,(original.width,25));d=ImageDraw.Draw(panel);d.text((4,4),'original',fill='black');d.text((original.width+4,4),'bounded proposal',fill='black');panel.save(out/'comparison.png')
 close=result.crop((145,0,215,135)).resize((560,1080),Image.Resampling.NEAREST);close.save(out/'blade-close-nearest.png')
 receipt={'status':'DRAFT_NOT_APPROVED','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'donor_sha256':hashlib.sha256(DONOR.read_bytes()).hexdigest(),'crop_from_generated_sheet':[443,0,887,443], 'donor_resize':list(original.size),'donor_translation_px':[-3,2],'mask_rectangle':[150,0,209,104],'gaussian_blur_radius':3,'changed_pixels':int(changed.sum()),'outside_mask_changed_pixels':outside,'limitations':['Donor generated independently; alignment is approximate and the blade seam is visible at inspection scale.','No corresponding pose landmarks or material continuity have been certified.','Only one pose of one direction; no alpha, cutouts, trail, animation or runtime binding.']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
