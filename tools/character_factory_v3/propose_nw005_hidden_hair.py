"""Propose same-frame hair underpainting only under fully opaque weapon pixels."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1';SRC=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW';O=P/'research/swordsman-nw005-head-ownership-20261103';DONOR=P/'painted-candidates/swordsman-nw005-hidden-hair-20261103/raw.png';ORDER=('WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 parts={}
 for role in ORDER:
  path=(O/(role+'.png')) if role in ('BodyCostume','HeadHair','Weapon') else (SRC/role/'005.png')
  parts[role]=np.array(Image.open(path).convert('RGBA'))
 rgb=np.array(Image.open(DONOR).convert('RGB').resize((80,80),Image.Resampling.LANCZOS));full=np.full((512,512,3),255,np.uint8);full[170:250,220:300]=rgb;yy,xx=np.indices((512,512));r,g,b=full.astype(int).transpose(2,0,1);warm=(r>g*1.2)&(g>b*1.2)&(r>90);m=(xx>=240)&(xx<264)&(yy>=187)&(yy<225)&(parts['Weapon'][:,:,3]==255)&(parts['HeadHair'][:,:,3]==0)&(full.min(axis=2)<235)&~warm
 head=parts['HeadHair'];head[m,:3]=full[m];head[m,3]=255
 original=np.array(Image.open(SRC/'Master/005.png').convert('RGBA'));canvas=Image.new('RGBA',(512,512))
 for role in ORDER:canvas.alpha_composite(Image.fromarray(parts[role]))
 visible=(original[:,:,3]>0)|(np.asarray(canvas)[:,:,3]>0);mismatch=int(np.any(original[visible]!=np.asarray(canvas)[visible],axis=1).sum())
 if mismatch:raise ValueError('underpaint changed visible master')
 out.mkdir(parents=True);Image.fromarray(head).save(out/'HeadHair-underpaint.png');Image.fromarray((m*255).astype('uint8')).save(out/'underpaint-mask.png');canvas.save(out/'recomposed.png');board=Image.new('RGB',(800,430),'#777');d=ImageDraw.Draw(board)
 for i,(name,arr) in enumerate((('head before',np.array(Image.open(O/'HeadHair.png').convert('RGBA'))),('head with hidden hair',head))):
  bg=Image.new('RGBA',(512,512),'#777');bg.alpha_composite(Image.fromarray(arr));board.paste(bg.crop((220,170,300,250)).resize((400,400),Image.Resampling.NEAREST).convert('RGB'),(i*400,25));d.text((i*400+2,2),name,fill='white')
 board.save(out/'comparison.png');proof={'status':'HIDDEN_HAIR_SINGLE_FRAME_NOT_APPROVED','donor_sha256':sha(DONOR),'master_sha256':sha(SRC/'Master/005.png'),'head_sha256':sha(O/'HeadHair.png'),'weapon_sha256':sha(O/'Weapon.png'),'script_sha256':sha(Path(__file__)),'underpaint_pixels':int(m.sum()),'visible_recomposition_mismatches':mismatch,'limitations':['Generated strands may not align with existing hairstyle; rectangle and color rules may include scarf or omit needed highlights.', 'Only fully opaque weapon pixels are underpainted; semi-transparent edges and uncovered surfaces remain unresolved.', 'No alternate weapon, adjacent frames, visual acceptance or gameplay.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
