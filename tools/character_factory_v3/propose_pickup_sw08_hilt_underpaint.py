"""Bounded single-frame glove underpaint from a generated donor.

Only new pixels concealed by fully opaque original weapon pixels are inserted.
The donor may have incorrect grasp anatomy and needs visual review.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-pickup-sw08-hilt-debris-20261029'
DONOR=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw08-hilt-underpaint-20261029/donor.png'
ORDER=('BodyCostume','HeadHair','Weapon');ROI=(370,540,405,580)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 layers={r:np.array(Image.open(BASE/'layers'/f'{r}.png').convert('RGBA')) for r in ORDER};master=Image.open(BASE/'master.png').convert('RGBA');donor=Image.open(DONOR).convert('RGB')
 if donor.size!=(1254,1254):raise ValueError('Unexpected donor canvas')
 tile=np.array(donor.resize((384,384),Image.Resampling.LANCZOS));canvas=np.full((768,768,3),255,np.uint8);canvas[257:641,192:576]=tile
 ys,xs=np.indices((768,768));scope=(xs>=ROI[0])&(xs<ROI[2])&(ys>=ROI[1])&(ys<ROI[3]);mask=scope&(layers['Weapon'][:,:,3]==255)&(layers['BodyCostume'][:,:,3]==0)&(layers['HeadHair'][:,:,3]==0)&(np.min(canvas,axis=2)<235)
 if not mask.any():raise ValueError('No bounded donor pixels selected')
 original={k:a.copy() for k,a in layers.items()};layers['BodyCostume'][mask,:3]=canvas[mask];layers['BodyCostume'][mask,3]=255
 composed=Image.new('RGBA',(768,768))
 for role in ORDER:composed.alpha_composite(Image.fromarray(layers[role]))
 if composed.tobytes()!=master.tobytes():raise ValueError('Original sword-on master changed')
 out.mkdir(parents=True);(out/'layers').mkdir();master.save(out/'master.png');Image.fromarray(mask.astype('uint8')*255,'L').save(out/'underpaint-mask.png')
 for role,a in layers.items():Image.fromarray(a,'RGBA').save(out/'layers'/f'{role}.png')
 def without_weapon(parts):
  im=Image.new('RGBA',(768,768))
  for role in ('BodyCostume','HeadHair'):im.alpha_composite(Image.fromarray(parts[role]))
  return im
 board=Image.new('RGB',(960,300),'#808080');draw=ImageDraw.Draw(board);crop=(350,525,465,605)
 for i,(title,im) in enumerate([('prior without weapon',without_weapon(original)),('underpaint without weapon',without_weapon(layers)),('unchanged sword on',composed)]):
  bg=Image.new('RGBA',(115,80),'#808080');bg.alpha_composite(im.crop(crop));board.paste(bg.convert('RGB').resize((320,240),Image.Resampling.NEAREST),(320*i,40));draw.text((i*320+4,6),title,fill='black')
 board.save(out/'underpaint-comparison.png');proof={'status':'DONOR_GLOVE_UNDERPAINT_PROPOSAL_NOT_APPROVED','source_master_sha256':sha(BASE/'master.png'),'donor_sha256':sha(DONOR),'roi_author_px':ROI,'inserted_pixels':int(mask.sum()),'restriction':'body and head transparent; original weapon alpha 255; donor nonwhite; fixed region','original_sword_on_master_exact':True,'source_modified':False,'runtime_admitted':False,'limitations':['The generated donor depicts an open hand, so grasp anatomy is not approved.','Near-transparent weapon edges and pixels outside the selected region are not repaired.','Original matte, head and weapon ownership remain provisional.','One frame only; no alternate weapon or other-view continuity.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
