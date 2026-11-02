"""Single-frame head swap review; not production art."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research';BODY=P/'swordsman-nw003-head-refined-20261102/BodyCostume.png';HEAD=P/'swordsman-nw003-alt-head-sam-20261102/head-2.png';WEAPON=P/'swordsman-nw003-hilt-edge-20261030/blade.png';SOURCE=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW/Master/003.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 body=Image.open(BODY).convert('RGBA');head=Image.new('RGBA',(512,512));head.paste(Image.open(HEAD).convert('RGBA').resize((170,170),Image.Resampling.LANCZOS),(180,130));weapon=Image.open(WEAPON).convert('RGBA');master=Image.open(SOURCE).convert('RGBA');result=body.copy();result.alpha_composite(head);result.alpha_composite(weapon);arr=np.asarray(result);b=np.asarray(body);union=(np.asarray(head)[:,:,3]>0)|(np.asarray(weapon)[:,:,3]>0);changed=np.any(arr!=b,axis=2)
 if np.any(changed&~union):raise ValueError('outside union altered')
 out.mkdir(parents=True);head.save(out/'alternate-head.png');result.save(out/'composite.png');board=Image.new('RGB',(1200,800));d=ImageDraw.Draw(board)
 for row,im in enumerate((master,result)):
  for col,c in enumerate(('white','#777','#222')):
   bg=Image.new('RGBA',(512,512),c);bg.alpha_composite(im);board.paste(bg.crop((180,130,350,300)).resize((400,400),Image.Resampling.LANCZOS).convert('RGB'),(col*400,row*400));d.text((col*400+2,row*400+2),'original' if row==0 else 'alternate head draft',fill='red')
 board.save(out/'comparison.png');proof={'status':'HEAD_SWAP_SINGLE_FRAME_NOT_APPROVED','body_sha256':sha(BODY),'head_sha256':sha(HEAD),'weapon_sha256':sha(WEAPON),'source_sha256':sha(SOURCE),'script_sha256':sha(Path(__file__)),'outside_union_difference':int((changed&~union).sum()),'limitations':['Generated head differs in position, size and facial features; registration and neck seam need review.', 'Segmentation uses a binary mask and may omit face or include background; source alpha and neckline are not approved.', 'Body is not underpainted for different hair shapes; only one pose/view and no runtime.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
