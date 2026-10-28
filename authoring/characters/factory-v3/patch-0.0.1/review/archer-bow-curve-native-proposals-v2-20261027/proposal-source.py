"""Native-image bow-curve segmentation proposals; never final weapon approval."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,sys
import numpy as np
import torch
sys.path.append('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages')
from scipy import ndimage
sys.path.insert(0,'/workspace/.tools/SAM2')
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
keys={
'male/SW':[[[294,186],[274,266],[303,239]],[[293,191],[276,266],[306,246]],[[294,104],[297,238],[319,179]],[[305,132],[294,250],[319,203]],[[294,187],[274,266],[304,240]]],
'male/NE':[[[224,127],[237,268],[207,200]],[[232,132],[239,278],[218,208]],[[224,100],[219,225],[198,164]],[[225,106],[232,250],[205,196]],[[224,126],[236,270],[208,200]]],
'male/SE':[[[191,190],[290,310],[227,241]],[[194,193],[286,309],[226,245]],[[220,80],[233,241],[212,173]],[[214,124],[285,294],[237,215]],[[190,191],[289,310],[226,243]]],
'female/SW':[[[301,180],[282,266],[309,232]],[[307,174],[291,271],[317,231]],[[315,83],[310,230],[333,164]],[[308,141],[302,260],[333,213]],[[303,181],[283,268],[311,234]]],
'female/NE':[[[226,122],[239,252],[212,195]],[[235,122],[244,258],[218,199]],[[238,86],[240,219],[220,154]],[[228,112],[231,252],[210,194]],[[227,123],[240,253],[213,195]]],
'female/SE':[[[179,151],[274,310],[214,234]],[[188,162],[273,309],[225,239]],[[220,101],[226,253],[212,188]],[[196,143],[257,288],[217,222]],[[179,153],[274,310],[214,234]]]}
b=Path('authoring/characters/factory-v3/patch-0.0.1');out=b/'review/archer-bow-curve-native-proposals-v2-20261027';out.mkdir(exist_ok=False);cp=Path('/workspace/.tools/SAM2/sam2.1_hiera_tiny.pt');torch.set_num_threads(3);predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(cp),device='cpu',apply_postprocessing=False));records=[];ticks=[0,4,8,11,15]
(out/'native-key-proposals.json').write_text(json.dumps({'indices':ticks,'points_order':['upper_tip','lower_tip','grip_reference'],'keys':keys,'annotation_status':'visual approximate seeds; source-image snapping and native review required'},indent=2)+'\n')
for key,anchors in keys.items():
 sex,view=key.split('/')
 for i in range(16):
  master=b/'review/archer-coherent-recovery-masters-v2-20261026'/sex/view/'Master'/f'{i:03d}.png';im=Image.open(master).convert('RGBA');a=np.array(im);r,g,z=a[:,:,:3].astype(float).transpose((2,0,1));alpha=a[:,:,3]>128;distance=ndimage.distance_transform_edt(alpha);yy,xx=np.indices(alpha.shape);points=np.array([[np.interp(i,ticks,[row[j][axis]for row in anchors])for axis in range(2)]for j in range(3)]);head=np.array(Image.open(b/'review/archer-remaining-view-head-complete-proposals-v6-20261027'/sex/view/f'{i:03d}.png'))[:,:,3]>0;warm=alpha&(r>g*1.15)&(g>z*1.05)&~head;thin=warm&(distance<4.5);record={'sex':sex,'view':view,'index':i,'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'approximate_native_reference_points':points.tolist(),'semantic_approved':False};records.append(record)
  try:
   positive=[]
   for tip_index,target in enumerate(points[:2]):
    scope=thin&(((xx-target[0])**2+(yy-target[1])**2)<42**2)&(abs(yy-target[1])<23);sy,sx=np.where(scope)
    if not len(sx):raise ValueError('No visible thin bow wood near proposed terminal')
    direction=1 if view=='SW'or(view=='SE'and tip_index==1)else-1;q=np.argmin((sx-target[0])**2+2*(sy-target[1])**2-direction*50*(sx-target[0]));positive.append([int(sx[q]),int(sy[q])])
   grip=points[2];inward=-1 if view=='SW'else 1;target=grip+np.array([12*inward,0]);scope=alpha&(distance>4)&(((xx-target[0])**2+(yy-target[1])**2)<20**2)&~head;sy,sx=np.where(scope)
   if not len(sx):raise ValueError('No unambiguous thick glove/arm negative near grip')
   q=np.argmin((sx-target[0])**2+(sy-target[1])**2);negative=[[int(sx[q]),int(sy[q])]];allpts=np.concatenate([np.array(positive),[grip]],axis=0);bounds=[max(0,int(allpts[:,0].min()-16)),max(0,int(allpts[:,1].min()-12)),min(512,int(allpts[:,0].max()+16)),min(512,int(allpts[:,1].max()+12))];crop=[max(0,bounds[0]-22),max(0,bounds[1]-18),min(512,bounds[2]+22),min(512,bounds[3]+18)];bg=Image.new('RGBA',im.size,'#ddd');bg.alpha_composite(im);predictor.set_image(np.array(bg.crop(crop).convert('RGB')));masks,scores,_=predictor.predict(point_coords=np.array(positive+negative)-np.array(crop[:2]),point_labels=np.array([1,1,0]),box=np.array(bounds)-np.array(crop[:2]*2),multimask_output=True);candidates=[];directory=out/sex/view;directory.mkdir(parents=True,exist_ok=True)
   for k,score in enumerate(scores):
    mask=np.zeros((512,512),bool);mask[crop[1]:crop[3],crop[0]:crop[2]]=masks[k];mask&=a[:,:,3]>0;mask&=~head;components,count=ndimage.label(mask,structure=np.ones((3,3)));keep={int(components[y,x])for x,y in positive if components[y,x]>0};mask&=np.isin(components,list(keep));area=int(mask.sum());away=mask&(((xx-grip[0])**2+(yy-grip[1])**2)>18**2);thick_fraction=float((away&(distance>4.5)).sum())/max(1,int(away.sum()));length=float(np.linalg.norm(np.array(positive[0])-positive[1]));valid=length*1.3<area<2200 and thick_fraction<.15 and all(mask[y,x]for x,y in positive)and all(not mask[y,x]for x,y in negative);candidates.append((float(score)if valid else-1,k,mask,area));(directory/'Candidates').mkdir(exist_ok=True);Image.fromarray(mask.astype('uint8')*255).save(directory/'Candidates'/f'{i:03d}-{k}.png')
   score,k,mask,area=max(candidates,key=lambda q:q[0]);record.update({'positive':positive,'negative':negative,'box':bounds,'crop':crop,'selected':k,'candidate_scores':[{'index':k,'score':float(scores[k]),'valid':s>=0,'area':n}for s,k,m,n in candidates]})
   if score<0:raise ValueError('No bow candidate meets native terminal/glove prompts')
   part=a.copy();part[~mask]=0;(directory/'BowCurve').mkdir(exist_ok=True);Image.fromarray(part).save(directory/'BowCurve'/f'{i:03d}.png');record['selected_area']=area;print('BOW_PROPOSED',key,i,area,flush=True)
  except ValueError as error:record['unresolved']=str(error);print('BOW_UNRESOLVED',key,i,str(error),flush=True)
(out/'receipt.json').write_text(json.dumps({'status':'BOW_CURVE_NATIVE_PROPOSALS_NOT_FULL_WEAPON_CUTOUTS','checkpoint_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'frames':records,'string_arrow_hand_ownership_completed':False,'runtime_admitted':False},indent=2)+'\n');(out/'proposal-source.py').write_bytes(Path(__file__).read_bytes())
