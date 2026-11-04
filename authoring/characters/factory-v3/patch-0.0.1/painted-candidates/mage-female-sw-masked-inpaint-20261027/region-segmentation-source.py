from pathlib import Path
from PIL import Image
import numpy as np,json,sys,torch
sys.path.insert(0,'/workspace/.tools/SAM2')
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
torch.set_num_threads(3)
b=Path('authoring/characters/factory-v3/patch-0.0.1');o=b/'painted-candidates/mage-female-sw-masked-inpaint-20261027';predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml','/workspace/.tools/SAM2/sam2.1_hiera_tiny.pt',device='cpu',apply_postprocessing=False));old=b/'review/mage-female-sw-canonical-pilot-20261027/Master/008.png';new=o/'registered-repaint.png';jobs=[('old-head',old,[325,310,410,395],[330,320,399,386],[[365,346],[350,345],[381,369]],[[404,340],[370,390]]),('old-weapon',old,[380,295,430,535],[390,310,418,520],[[404,340],[402,380],[405,450],[407,500]],[[383,365],[398,403],[390,480]]),('new-weapon',new,[325,270,385,530],[335,275,366,512],[[351,300],[352,360],[353,430],[355,490]],[[367,350],[372,426],[346,398],[345,480]])];proof=[]
for name,path,crop,box,pos,neg in jobs:
 im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'#ddd');bg.alpha_composite(im);predictor.set_image(np.array(bg.crop(crop).convert('RGB')));masks,scores,_=predictor.predict(point_coords=np.array(pos+neg,np.float32)-np.array(crop[:2]),point_labels=np.array([1]*len(pos)+[0]*len(neg)),box=np.array(box)-np.array(crop[:2]*2),multimask_output=True);details=[]
 for k,(mask,score) in enumerate(zip(masks,scores)):
  full=np.zeros((768,768),bool);full[crop[1]:crop[3],crop[0]:crop[2]]=mask;a=np.array(im);a[~full]=0;Image.fromarray(a).save(o/f'{name}-proposal{k}.png');v=Image.new('RGBA',im.size,'#ddd');v.alpha_composite(Image.fromarray(a));v.crop(crop).resize(((crop[2]-crop[0])*4,(crop[3]-crop[1])*4),Image.Resampling.NEAREST).convert('RGB').save(o/f'{name}-proposal{k}.jpg');details.append({'index':k,'score':float(score),'area':int(full.sum()),'positive_inside':[bool(full[y,x])for x,y in pos],'negative_inside':[bool(full[y,x])for x,y in neg]})
 proof.append({'name':name,'source':str(path),'crop':crop,'box':box,'positive':pos,'negative':neg,'proposals':details});print(name,details,flush=True)
(o/'semantic-proposals.json').write_text(json.dumps(proof,indent=2)+'\n')
