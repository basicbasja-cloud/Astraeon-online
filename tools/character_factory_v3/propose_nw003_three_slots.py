"""Partition one no-weapon master into same-frame body/head plus original weapon."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research'
BASE=P/'swordsman-nw003-hilt-edge-20261030'
MASK=P/'swordsman-nw003-head-refined-20261102/head-mask.png'
SOURCE=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW/Master/003.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('use fresh output')
 under=np.asarray(Image.open(BASE/'underpaint-no-blade.png').convert('RGBA')); mask=np.asarray(Image.open(MASK).convert('L'))>0; blade=Image.open(BASE/'blade.png').convert('RGBA');original=np.asarray(Image.open(SOURCE).convert('RGBA'));head=np.zeros_like(under);body=np.zeros_like(under);head[mask]=under[mask];body[~mask]=under[~mask]
 composed=Image.fromarray(body);composed.alpha_composite(Image.fromarray(head));composed.alpha_composite(blade);delta=np.any(np.asarray(composed)!=original,axis=2)
 if delta.any():raise ValueError('master reconstruction failed')
 out.mkdir(parents=True);Image.fromarray(body).save(out/'BodyCostume.png');Image.fromarray(head).save(out/'HeadHair.png');blade.save(out/'Weapon.png');composed.save(out/'recomposed.png')
 board=Image.new('RGB',(1200,420),'#777');d=ImageDraw.Draw(board)
 for i,(label,im) in enumerate((('BodyCostume',Image.fromarray(body)),('HeadHair',Image.fromarray(head)),('Weapon',blade))):
  bg=Image.new('RGBA',(512,512),'#777');bg.alpha_composite(im);board.paste(bg.crop((210,145,310,220)).resize((400,300),Image.Resampling.NEAREST).convert('RGB'),(400*i,40));d.text((400*i+3,5),label,fill='white')
 board.save(out/'slots.png');proof={'status':'THREE_SLOTS_SINGLE_FRAME_NOT_APPROVED','underpaint_sha256':sha(BASE/'underpaint-no-blade.png'),'mask_sha256':sha(MASK),'weapon_sha256':sha(BASE/'blade.png'),'source_sha256':sha(SOURCE),'script_sha256':sha(Path(__file__)),'visible_rgba_difference_pixels':int(delta.sum()),'limitations':['Head mask is a heuristic proposal; neck and boundary ownership require manual review.', 'Weapon selection includes glove/costume edge pixels; hand occlusion and underpainting are not validated.', 'Exact pixel reconstruction does not prove semantic correctness or a usable asset swap.', 'Only one frame and one view; no gameplay or complete action.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
