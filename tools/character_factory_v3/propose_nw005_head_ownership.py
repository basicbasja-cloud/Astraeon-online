"""Move suggested visible same-frame hair ownership without changing the composite."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW';MASK=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw005-head-sam-20261103/mask2.png';ORDER=('WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 parts={}
 for role in ORDER:
  with Image.open(SRC/role/'005.png') as im:parts[role]=np.array(im.convert('RGBA'))
 master=np.array(Image.open(SRC/'Master/005.png').convert('RGBA'));sam=np.array(Image.open(MASK).convert('L'))>0;r,g,b=master[:,:,:3].astype(int).transpose(2,0,1);warm=(r>g*1.2)&(g>b*1.2)&(r>90);head=parts['HeadHair'];moves={}
 # The original mask plus SAM-selected nonwarm pixels; no newly invented pixels.
 for role in ('BodyCostume','Weapon'):
  layer=parts[role];move=sam&~warm&(layer[:,:,3]>0)
  if np.any(head[:,:,3][move]>0):raise ValueError('overlapping ownership')
  head[move]=layer[move];layer[move]=0;moves[role]=int(move.sum())
 # Conservative warm pixels below this rear-view head are scarf, returned to body.
 move=warm&(head[:,:,3]>0);body=parts['BodyCostume']
 if np.any(body[:,:,3][move]>0):raise ValueError('scarf ownership overlaps body')
 body[move]=head[move];head[move]=0;moves['head_to_body_warm']=int(move.sum())
 canvas=Image.new('RGBA',(512,512))
 for role in ORDER:canvas.alpha_composite(Image.fromarray(parts[role]))
 a=np.asarray(canvas);visible=(a[:,:,3]>0)|(master[:,:,3]>0)
 if not np.array_equal(a[visible],master[visible]) or not np.array_equal(a[:,:,3],master[:,:,3]):raise ValueError('visible recomposition mismatch')
 out.mkdir(parents=True)
 for role in ('BodyCostume','HeadHair','Weapon'):Image.fromarray(parts[role]).save(out/(role+'.png'))
 canvas.save(out/'recomposed.png');board=Image.new('RGB',(1200,440),'#777');draw=ImageDraw.Draw(board)
 for i,(name,arr) in enumerate((('old head',np.array(Image.open(SRC/'HeadHair/005.png').convert('RGBA'))),('proposed head',head),('proposed weapon',parts['Weapon']))):
  bg=Image.new('RGBA',(512,512),'#777');bg.alpha_composite(Image.fromarray(arr));board.paste(bg.crop((220,170,300,250)).resize((400,400),Image.Resampling.NEAREST).convert('RGB'),(i*400,35));draw.text((i*400+3,3),name,fill='white')
 board.save(out/'comparison.png');proof={'status':'NW005_HEAD_OWNERSHIP_PROPOSAL_NOT_APPROVED','input_sha256':{role:sha(SRC/role/'005.png') for role in ORDER},'master_sha256':sha(SRC/'Master/005.png'),'mask_sha256':sha(MASK),'script_sha256':sha(Path(__file__)),'moves':moves,'visible_rgba_mismatch':0,'limitations':['SAM and warm-color rules are provisional; hair/sword and scarf boundaries may still be wrong.', 'Hidden hair behind the sword is not authored; hiding the weapon cannot prove a swappable head.', 'One frame only; animation, variants, remaining views and gameplay are not approved.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
