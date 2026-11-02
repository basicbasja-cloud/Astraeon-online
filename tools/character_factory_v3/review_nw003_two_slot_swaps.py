"""Review four single-frame head/weapon combinations; no runtime intake."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research';BODY=P/'swordsman-nw003-body-edge-cleanup-20261102/BodyCostume.png';HEAD0=P/'swordsman-nw003-three-slots-20261102/HeadHair.png';HEAD1=P/'swordsman-nw003-alt-head-swap-20261102/alternate-head.png';WEAPON0=P/'swordsman-nw003-three-slots-20261102/Weapon.png';WEAPON1=P/'swordsman-nw003-alt-sword-refined-20261030/alternate-weapon.png';HAND1=P/'swordsman-nw003-alt-sword-refined-20261030/hand-occluder.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 paths={'body':BODY,'head_original':HEAD0,'head_alternate':HEAD1,'weapon_original':WEAPON0,'weapon_alternate':WEAPON1,'hand_alternate':HAND1};im={k:Image.open(v).convert('RGBA') for k,v in paths.items()};out.mkdir(parents=True);boards=[];results={};composites={}
 for h,w in ((0,0),(1,0),(0,1),(1,1)):
  canvas=im['body'].copy();canvas.alpha_composite(im['head_alternate' if h else 'head_original']);canvas.alpha_composite(im['weapon_alternate' if w else 'weapon_original']);
  if w:canvas.alpha_composite(im['hand_alternate'])
  name=f'head{h}-weapon{w}';composites[(h,w)]=np.asarray(canvas).copy();canvas.save(out/f'{name}.png');results[name]=hashlib.sha256((out/f'{name}.png').read_bytes()).hexdigest();bg=Image.new('RGBA',(512,512),'#777');bg.alpha_composite(canvas);frames=bg.crop((155,120,365,330)).resize((384,384),Image.Resampling.LANCZOS).convert('RGB');boards.append((name,frames))
 head_union=(np.asarray(im['head_original'])[:,:,3]>0)|(np.asarray(im['head_alternate'])[:,:,3]>0);weapon_union=(np.asarray(im['weapon_original'])[:,:,3]>0)|(np.asarray(im['weapon_alternate'])[:,:,3]>0)|(np.asarray(im['hand_alternate'])[:,:,3]>0);violations={}
 for w in (0,1):violations[f'head_change_weapon{w}']=int((np.any(composites[(0,w)]!=composites[(1,w)],axis=2)&~head_union).sum())
 for h in (0,1):violations[f'weapon_change_head{h}']=int((np.any(composites[(h,0)]!=composites[(h,1)],axis=2)&~weapon_union).sum())
 if any(violations.values()):raise ValueError(f'slot changes outside union: {violations}')
 board=Image.new('RGB',(768,816),'#777');d=ImageDraw.Draw(board)
 for i,(name,frame) in enumerate(boards):
  x=(i%2)*384;y=(i//2)*408;board.paste(frame,(x,y+24));d.text((x+4,y+4),name,fill='white')
 board.save(out/'comparison.png');frames=[]
 for name,frame in boards:
  picture=Image.new('RGB',(384,408),'#777');picture.paste(frame,(0,24));ImageDraw.Draw(picture).text((4,4),name+' / still',fill='white');frames.append(picture)
 frames[0].save(out/'still-toggle.gif',save_all=True,append_images=frames[1:],duration=1200,loop=0,disposal=2)
 proof={'status':'TWO_SLOT_SINGLE_FRAME_NOT_APPROVED','inputs_sha256':{k:sha(v) for k,v in paths.items()},'script_sha256':sha(Path(__file__)),'outputs_sha256':results,'outside_slot_union_differences':violations,'limitations':['Head/weapon masks and hand occlusion contain uncertain pixels; head/collar and blade edges require visual review.', 'No same-frame underpainting exists for every possible variant shape.', 'Four still combinations do not validate animation, direction coverage, gameplay or a complete character.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
