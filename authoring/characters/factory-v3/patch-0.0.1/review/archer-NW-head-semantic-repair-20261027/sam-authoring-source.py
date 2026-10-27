import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
import torch
sys.path.insert(0,'/workspace/.tools/SAM2')
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
torch.set_num_threads(3)
b=Path('/workspace/Astraeon-online/authoring/characters/factory-v3/patch-0.0.1/review');o=b/'archer-NW-head-semantic-repair-20261027';o.mkdir(exist_ok=True);im=Image.open(b/'archer-coherent-recovery-masters-v2-20261026/male/NW/Master/009.png').convert('RGBA');bg=Image.new('RGBA',im.size,'#ddd');bg.alpha_composite(im);crop=(200,140,300,225);rgb=np.array(bg.crop(crop).convert('RGB'));p=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml','/workspace/.tools/SAM2/sam2.1_hiera_tiny.pt',device='cpu',apply_postprocessing=False));p.set_image(rgb);pts=np.array([[235,172],[245,178],[232,160],[260,165],[275,158],[259,189],[218,198],[233,202]],np.float32)-np.array(crop[:2]);labels=np.array([1,1,1,0,0,0,0,0]);m,s,_=p.predict(point_coords=pts,point_labels=labels,box=np.array([215,150,258,190])-np.array(crop[:2]*2),multimask_output=True)
for k,(mask,score) in enumerate(zip(m,s)):
 full=np.zeros((512,512),bool);full[crop[1]:crop[3],crop[0]:crop[2]]=mask;a=np.array(im);a[~full]=0;Image.fromarray(a).save(o/f'male009-proposal{k}.png');v=Image.new('RGBA',(512,512),'#ddd');v.alpha_composite(Image.fromarray(a));v.crop((210,150,280,215)).resize((700,650)).convert('RGB').save(o/f'male009-proposal{k}.jpg');print(k,float(score),int(full.sum()))
(o/'sam-prompts.json').write_text(json.dumps({'crop':crop,'points':(pts+np.array(crop[:2])).tolist(),'labels':labels.tolist(),'scores':s.tolist(),'source':'archer-coherent-recovery-masters-v2-20261026/male/NW/Master/009.png'},indent=2)+'\n')
