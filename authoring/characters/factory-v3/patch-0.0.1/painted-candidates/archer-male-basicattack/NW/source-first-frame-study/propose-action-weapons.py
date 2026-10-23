from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
import torch
sys.path.insert(0,'/workspace/.tools/MobileSAM');from mobile_sam import sam_model_registry,SamPredictor
torch.set_num_threads(2);checkpoint=Path('/workspace/.tools/MobileSAM/weights/mobile_sam.pt');model=sam_model_registry['vit_t'](checkpoint=None);model.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=True));model.eval();predictor=SamPredictor(model)
p=Path('authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW/source-first-frame-study');out=p/'action-weapon-proposals';out.mkdir(exist_ok=True);rows=[]
for i,pos,neg,box in [(8,[[443,68],[456,125],[450,232],[443,301]],[[455,181],[389,269],[420,210]],[432,50,484,330]),(11,[[475,140],[448,212],[407,337],[401,382]],[[420,283],[403,367],[385,350]],[392,125,486,395])]:
 source=p/'sequence/detail'/f'{i:03d}.png';im=Image.open(source).convert('RGBA');a=np.array(im);bg=Image.new('RGBA',im.size,'#e8e8e8');bg.alpha_composite(im);predictor.set_image(np.array(bg.convert('RGB')));points=np.array(pos+neg,np.float32);labels=np.array([1]*len(pos)+[0]*len(neg));masks,scores,_=predictor.predict(point_coords=points,point_labels=labels,box=np.array(box),multimask_output=True)
 sheet=Image.new('RGBA',(1200,720),'#e8e8e8');d=ImageDraw.Draw(sheet)
 for j,(mask,score)in enumerate(zip(masks,scores)):
  mask&=a[:,:,3]>0;weapon=a.copy();weapon[~mask]=0;body=a.copy();body[mask]=0
  for role,part in [('Weapon',weapon),('Remainder',body)]:Image.fromarray(part).save(out/f'{i:03d}-{role}-{j}.png')
  for k,part in enumerate([weapon,body]):sheet.alpha_composite(Image.fromarray(part).crop((380,40,500,400)).resize((200,600)),(j*400+k*200,30))
  d.text((j*400+4,4),f'{i} proposal{j} score {score:.3f}',fill='black')
 sheet.save(out/f'{i:03d}-comparison.png');rows.append({'index':i,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'positive':pos,'negative':neg,'box':box,'scores':scores.tolist()})
(out/'receipt.json').write_text(json.dumps({'status':'SEMANTIC_WEAPON_PROPOSALS_NOT_APPROVED','frames':rows,'checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'runtime_admitted':False},indent=2)+'\n')
