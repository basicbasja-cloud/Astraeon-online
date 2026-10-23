from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,cv2
p=Path('authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW/source-first-frame-study');polygons={0:[[300,170],[435,170],[435,230],[421,245],[407,250],[398,265],[386,270],[369,260],[345,255],[335,247],[329,240],[319,232]],8:[[300,175],[394,175],[401,195],[402,205],[399,222],[397,240],[390,249],[387,258],[380,270],[366,269],[345,265],[331,257],[318,242],[307,225]],11:[[310,170],[437,170],[437,228],[422,245],[411,251],[402,265],[388,270],[370,260],[349,256],[340,248],[333,240],[325,231]]};out=p/'manual-head-seeds';rows=[]
for i,polygon in polygons.items():
 master_path=p/'sequence/detail'/f'{i:03d}.png';master=Image.open(master_path).convert('RGBA');a=np.array(master);region=Image.new('L',master.size);ImageDraw.Draw(region).polygon(polygon,fill=255);mask=(np.array(region)>0)&(a[:,:,3]>0);rgb=a[:,:,:3].astype(float);r,g,b=rgb.transpose(2,0,1)
 # Explicit chestnut-hair/green-collar boundary aid, limited to the drawn polygon.
 collar=(g>=r*.9)&(g>b*1.1)&(r<180);mask&=~collar
 if i==8:
  yy,xx=np.indices(mask.shape);string=(rgb.min(2)>175)&(rgb.max(2)-rgb.min(2)<50)&(xx>385)&(yy>180);mask&=~string
 count,labels=cv2.connectedComponents((mask&(a[:,:,3]>16)).astype(np.uint8));areas=np.bincount(labels.ravel());areas[0]=0;main=labels==areas.argmax();near=cv2.dilate(main.astype(np.uint8),np.ones((7,7),np.uint8))>0;mask&=near
 head=a.copy();head[~mask]=0;body=a.copy();body[mask]=0
 for role,arr in [('HeadHair',head),('BodyCostume',body)]:folder=out/role;folder.mkdir(parents=True,exist_ok=True);Image.fromarray(arr).save(folder/f'{i:03d}.png')
 combined=np.array(Image.alpha_composite(Image.fromarray(body),Image.fromarray(head)));visible=a[:,:,3]>0
 if not np.array_equal(combined[visible],a[visible]):raise ValueError('Master changed')
 rows.append({'index':i,'polygon':polygon,'master_sha256':hashlib.sha256(master_path.read_bytes()).hexdigest(),'head_pixels':int(mask.sum()),'master_pixel_changes':0})
(out/'receipt.json').write_text(json.dumps({'status':'MANUAL_VISIBLE_HEAD_OWNERSHIP_PROPOSAL','frames':rows,'identity_specific_collar_color_guard':True,'manual_string_overlap_exclusion_frame8':True,'hidden_surfaces_authored':False,'runtime_admitted':False},indent=2)+'\n')
(p/'manual-head-seed-polygons.json').write_text(json.dumps(polygons,indent=2)+'\n')
# Readability review, always composite on grey before comparison.
review=Image.new('RGBA',(1320,600),'#e8e8e8');d=ImageDraw.Draw(review)
for j,i in enumerate(polygons):
 for k,role in enumerate(['HeadHair','BodyCostume']):review.alpha_composite(Image.open(out/role/f'{i:03d}.png').crop((280,170,500,320)).resize((440,300)),(j*440,k*300));d.text((j*440+5,k*300+5),f'{i} {role}',fill='black')
review.save(out/'review.png')
