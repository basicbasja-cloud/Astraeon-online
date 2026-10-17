from pathlib import Path
import json,time,hashlib
import torch,numpy as np
from PIL import Image,ImageDraw
from mobile_sam import sam_model_registry,SamPredictor
torch.set_num_threads(2);torch.set_num_interop_threads(1)
root=Path.cwd();checkpoint=root/'work/free-mask-model/source/weights/mobile_sam.pt'
model=sam_model_registry['vit_t'](checkpoint=None)
state=torch.load(checkpoint,map_location='cpu',weights_only=True);model.load_state_dict(state,strict=True);model.eval();predictor=SamPredictor(model)
rows=[]
for i,box,points,labels in [(0,[85,65,199,151],[[142,108],[142,137],[108,115],[179,111],[141,161],[107,151],[181,148]],[1,1,1,1,0,0,0]),(7,[80,143,188,230],[[140,175],[140,212],[140,225],[124,217],[159,219],[168,207],[102,189],[173,185],[145,237],[181,213],[193,187]],[1,1,1,1,1,1,1,1,0,0,0])]:
 p=root/f'research/sprite-animation/whole-body-v58/frames/full/{i:02}.png';full=Image.open(p).convert('RGBA');bg=Image.new('RGBA',full.size,'#343941');bg.alpha_composite(full);t=time.time();predictor.set_image(np.array(bg.convert('RGB')))
 masks,scores,logits=predictor.predict(point_coords=np.array(points),point_labels=np.array(labels),box=np.array(box),multimask_output=True)
 board=Image.new('RGB',(full.width*4,full.height+30),'#343941');board.paste(bg,(0,30));d=ImageDraw.Draw(board);d.text((5,5),f'full / {i}',fill='white')
 for j,(mask,score) in enumerate(zip(masks,scores)):
  head=Image.composite(full,Image.new('RGBA',full.size),Image.fromarray(mask.astype('uint8')*255));h=Image.new('RGBA',full.size,'#343941');h.alpha_composite(head);board.paste(h,((j+1)*full.width,30));d.text(((j+1)*full.width+5,5),f'mask {j} / score {score:.3f}',fill='white');head.save(root/f'work/all-actions-v61/sam-second/{i:02}-{j}.png')
 board.save(root/f'work/all-actions-v61/sam-second/board-{i:02}.jpg');rows.append({'frame':i,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'box':box,'points':points,'labels':labels,'scores':scores.tolist(),'seconds':time.time()-t})
 print(i,rows[-1]['seconds'],scores,flush=True)
(root/'work/all-actions-v61/sam-second/results.json').write_text(json.dumps({'checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'rows':rows},indent=2)+'\n')
