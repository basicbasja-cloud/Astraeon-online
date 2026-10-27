from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,sys
import torch
sys.path.insert(0,'/workspace/.tools/SAM2')
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
torch.set_num_threads(3)
b=Path('authoring/characters/factory-v3/patch-0.0.1');p=b/'painted-candidates/mage-female-single-frame-trace-20261027';o=b/'review/mage-female-target-gaze-head-asset-v2-20261027';o.mkdir(exist_ok=True);raw=Image.open(p/'raw000.png').convert('RGBA');crop=[380,240,690,560];box=[420,270,642,510];positive=[[520,370],[470,380],[608,410],[580,460]];negative=[[650,400],[555,525],[450,490]]
if any(raw.getpixel(tuple(q))[3]<128 for q in positive):raise ValueError('A foreground positive must lie on visible source pixels')
checkpoint=Path('/workspace/.tools/SAM2/sam2.1_hiera_tiny.pt');model=build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False);predictor=SAM2ImagePredictor(model);bg=Image.new('RGBA',raw.size,'#ddd');bg.alpha_composite(raw);predictor.set_image(np.array(bg.crop(crop).convert('RGB')));masks,scores,_=predictor.predict(point_coords=np.array(positive+negative)-np.array(crop[:2]),point_labels=np.array([1]*len(positive)+[0]*len(negative)),box=np.array(box)-np.array(crop[:2]*2),multimask_output=True);contact=Image.new('RGBA',(930,320),'#ddd');records=[]
for i,score in enumerate(scores):
 full=np.zeros(raw.size[::-1],bool);full[crop[1]:crop[3],crop[0]:crop[2]]=masks[i];full&=np.array(raw)[:,:,3]>0;mask=Image.fromarray(full.astype('uint8')*255);mask.save(o/f'proposal{i}-mask.png');a=np.array(raw);a[~full]=0;im=Image.fromarray(a);im.save(o/f'proposal{i}-HeadHair-raw.png');contact.alpha_composite(im.crop(crop),(i*310,0));ImageDraw.Draw(contact).text((i*310+3,2),f'{i}: {score:.4f}',fill='black');records.append({'index':i,'score':float(score),'pixels':int(full.sum()),'bbox':mask.getbbox(),'includes_positive':[bool(full[y,x])for x,y in positive],'includes_negative':[bool(full[y,x])for x,y in negative]})
contact.convert('RGB').save(o/'head-proposals.jpg',quality=98);(o/'proposal-receipt.json').write_text(json.dumps({'raw_master_sha256':hashlib.sha256((p/'raw000.png').read_bytes()).hexdigest(),'checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'crop':crop,'box':box,'positive':positive,'negative':negative,'proposals':records,'head_pose_family_reference':'research/target-facing-mage-gaze-20261027/head-pose-family-study.json / SW / pose0','semantic_approved':False,'neck_backfill_authored':False,'runtime_admitted':False},indent=2)+'\n');(o/'proposal-source.py').write_bytes(Path(__file__).read_bytes());print(records)
