from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_opening,label
import numpy as np,json,hashlib
p=Path('authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW/source-first-frame-study');out=p/'action-layer-seeds';out.mkdir(exist_ok=True);rows=[];corrections=[]
for i in [0,8,9,11,15]:
 master_path=p/'sequence/detail'/f'{i:03d}.png';a=np.array(Image.open(master_path));yy,xx=np.indices(a.shape[:2]);head=np.array(Image.open(p/'manual-head-seeds/HeadHair'/f'{0 if i in [0,15] else 8 if i in [8,9] else 11:03d}.png'))[:,:,3]>0
 if i in [0,15]:weapon=np.array(Image.open(p/'ready-cutout-study/Weapon'/f'{i:03d}.png'))[:,:,3]>0
 else:
  source=p/'action-weapon-proposals'/f'{8 if i==9 else i:03d}-Weapon-0.png';weapon=np.array(Image.open(source))[:,:,3]>0
  protect=Image.new('L',(768,768));d=ImageDraw.Draw(protect);lines=Image.new('L',(768,768));ld=ImageDraw.Draw(lines)
  if i in [8,9]:
   d.polygon([(439,174),(446,169),(458,167),(467,171),(471,180),(465,193),(452,197),(444,192)],fill=255);d.ellipse((378,251,400,278),fill=255)
   ld.line([(443,65),(397,253),(443,319)],fill=255,width=3);ld.line([(397,253),(480,131)],fill=255,width=3)
  else:
   d.polygon([(407,274),(416,266),(426,265),(437,274),(438,287),(431,298),(418,303),(409,297)],fill=255);d.polygon([(382,345),(406,346),(430,350),(432,378),(413,384),(393,377)],fill=255)
  weapon=(binary_dilation(weapon,iterations=2)|(np.array(lines)>0))&(np.array(protect)==0)
 if i not in [0,15]:
  body_core=(a[:,:,3]>16)&~weapon&~head;opened=binary_opening(body_core,iterations=2);near=binary_dilation(opened,iterations=2);r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);thin=(a[:,:,3]>0)&~weapon&~head&~near&(xx>392)&(xx<490)&(yy>50)&(yy<395)&(np.array(protect)==0)&((r-b>35)|(r<100));weapon|=thin
 weapon&=a[:,:,3]>0;overlap=int((head&weapon).sum());weapon&=~head
 for role,mask in [('HeadHair',head),('Weapon',weapon)]:
  folder=out/role;folder.mkdir(exist_ok=True);part=a.copy();part[~mask]=0;Image.fromarray(part).save(folder/f'{i:03d}.png')
 body=a.copy();body[head|weapon]=0;folder=out/'BodyCostume';folder.mkdir(exist_ok=True);Image.fromarray(body).save(folder/f'{i:03d}.png')
 corrections.append({'index':i,'masks':{r:f'action-layer-seeds/{r}/{i:03d}.png'for r in ['HeadHair','Weapon']}});rows.append({'index':i,'master_sha256':hashlib.sha256(master_path.read_bytes()).hexdigest(),'head_weapon_overlap_pixels_kept_in_reviewed_head':overlap,'visible_weapon_pixels':int(weapon.sum())})
(p/'action-layer-seeds.json').write_text(json.dumps({'roles':['HeadHair','Weapon'],'corrections':corrections},indent=2)+'\n');(out/'receipt.json').write_text(json.dumps({'status':'REVIEWED_COORDINATE_ASSISTED_SEED_PROPOSALS_NOT_FINAL_MASKS','frames':rows,'runtime_admitted':False},indent=2)+'\n');print(json.dumps(rows))
