"""Bounded full-master sword repair experiment. This output is not approved."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates';SRC=P/'swordsman-hit-sw000-bounded-repair-20261102/draft.png';DONOR=P/'swordsman-hit-sw000-single-repair-v3-20261102/raw.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 src=Image.open(SRC).convert('RGBA');donor=Image.open(DONOR).convert('RGB').resize((320,320),Image.Resampling.LANCZOS)
 if src.size!=(768,768):raise ValueError('unexpected master size')
 full=Image.new('RGB',(768,768),'white');full.paste(donor,(224,260));a=np.array(src);b=np.asarray(full);yy,xx=np.indices(a.shape[:2]);mask=(xx>=388)&(xx<435)&(yy>=370)&(yy<430)&(a[:,:,3]>=240);candidate=a.copy();candidate[mask,:3]=b[mask]
 if np.any(candidate[~mask]!=a[~mask]):raise ValueError('outside mask changed')
 out.mkdir(parents=True);Image.fromarray(candidate).save(out/'candidate.png');Image.fromarray(mask.astype('uint8')*255).save(out/'mask.png');board=Image.new('RGB',(900,450),'#777');draw=ImageDraw.Draw(board)
 for i,im in enumerate((src,Image.fromarray(candidate))):
  bg=Image.new('RGBA',(768,768),'#777');bg.alpha_composite(im);board.paste(bg.crop((310,310,460,460)).resize((450,450),Image.Resampling.NEAREST).convert('RGB'),(450*i,0));draw.text((450*i+3,3),'original' if i==0 else 'bounded draft / rejected',fill='red')
 board.save(out/'comparison.png');proof={'status':'BOUNDED_HIT_PATCH_REJECTED','source_sha256':sha(SRC),'donor_sha256':sha(DONOR),'script_sha256':sha(Path(__file__)),'mask_pixels':int(mask.sum()),'outside_mask_difference':0,'limitations':['Visible white wedge near arm and broken sword continuity: donor and master colors/alpha do not match.', 'The alpha threshold does not establish correct matte; landmarks and source hand/sword grip remain unverified.', 'No production, full sequence, cutout or gameplay approval.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
