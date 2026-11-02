"""Refine one draft head mask using nearby original labels and face-colored pixels."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,label
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research';BASE=P/'swordsman-nw003-hilt-edge-20261030/underpaint-no-blade.png';SAM=P/'swordsman-nw003-head-sam-20261102/mask-2.png';OLD=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW/HeadHair/003.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 src=np.asarray(Image.open(BASE).convert('RGBA'));sam=np.asarray(Image.open(SAM).convert('L'))>0;old=np.asarray(Image.open(OLD).convert('RGBA'))[:,:,3]>0;mask=sam|(old&binary_dilation(sam,iterations=2));r,g,b=src[:,:,:3].astype(int).transpose(2,0,1);yy,xx=np.indices(mask.shape);skin=(xx>=249)&(xx<=266)&(yy>=193)&(yy<=207)&(r>110)&(r>g*1.1)&(g>b*1.1)&(src[:,:,3]>0);components,n=label(skin|mask,np.ones((3,3)));ids=np.unique(components[mask]);skin_connected=skin&np.isin(components,ids[ids!=0]);mask|=skin_connected
 # Tiny original alpha fringe above the face belongs to the head silhouette.
 fringe=(xx>=220)&(xx<272)&(yy>=150)&(yy<190)&(src[:,:,3]>0)&~mask;mask|=fringe
 head=np.zeros_like(src);body=np.zeros_like(src);head[mask]=src[mask];body[~mask]=src[~mask];out.mkdir(parents=True);Image.fromarray((mask*255).astype('uint8')).save(out/'head-mask.png');Image.fromarray(head).save(out/'HeadHair.png');Image.fromarray(body).save(out/'BodyCostume.png');board=Image.new('RGB',(800,340),'#777');d=ImageDraw.Draw(board)
 for i,(name,arr) in enumerate((('body',body),('head',head))):
  bg=Image.new('RGBA',(512,512),'#777');bg.alpha_composite(Image.fromarray(arr));board.paste(bg.crop((210,145,310,220)).resize((400,300),Image.Resampling.NEAREST).convert('RGB'),(400*i,35));d.text((i*400+3,3),name,fill='white')
 board.save(out/'slots.png');proof={'status':'REFINED_HEAD_PROPOSAL_NOT_APPROVED','source_sha256':sha(BASE),'sam_sha256':sha(SAM),'old_sha256':sha(OLD),'script_sha256':sha(Path(__file__)),'added_pixels':int((mask&~sam).sum()),'limitations':['Color and proximity rules may include scarf, arm or omit skin; manual semantic review is required.', 'No hidden neck surfaces, head swap, complete animation or gameplay is approved.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
