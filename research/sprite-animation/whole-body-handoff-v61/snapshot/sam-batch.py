from pathlib import Path
import json,time,hashlib
import torch,numpy as np
from scipy.ndimage import binary_fill_holes
from PIL import Image,ImageDraw
from mobile_sam import sam_model_registry,SamPredictor
torch.set_num_threads(2);torch.set_num_interop_threads(1);root=Path.cwd();out=root/'work/all-actions-v61/sam-batch';out.mkdir(exist_ok=True)
model=sam_model_registry['vit_t'](checkpoint=None);model.load_state_dict(torch.load(root/'work/free-mask-model/source/weights/mobile_sam.pt',map_location='cpu',weights_only=True),strict=True);model.eval();predictor=SamPredictor(model)
crowns=[72,90,107,110,115,119,128,148,78,63,64,56,43,46,47,44];chins=[150,170,185,189,196,203,212,230,162,144,146,139,123,127,128,124];centers=[143,146,141,142,140,142,146,145,142,142,143,144,143,147,147,147];rows=[]
board=Image.new('RGB',(281*4,210*4),'#343941');draw=ImageDraw.Draw(board)
for i,(top,chin,cx) in enumerate(zip(crowns,chins,centers)):
 p=root/f'research/sprite-animation/whole-body-v58/frames/full/{i:02}.png';full=Image.open(p).convert('RGBA');bg=Image.new('RGBA',full.size,'#343941');bg.alpha_composite(full)
 points=[[cx,top+30],[cx-30,top+45],[cx+30,top+35],[cx,top+58],[cx,chin-16],[cx,chin-5],[cx-16,chin-13],[cx+16,chin-14],[cx,chin+8],[cx-53,chin+4],[cx+53,chin+4],[cx+62,chin-30]];labels=[1]*8+[0]*4;box=[cx-65,top-4,cx+60,chin+3]
 t=time.time();predictor.set_image(np.array(bg.convert('RGB')));masks,scores,_=predictor.predict(point_coords=np.array(points),point_labels=np.array(labels),box=np.array(box),multimask_output=True)
 options=[]
 for j,mask in enumerate(masks):
  filled=binary_fill_holes(mask);violations=sum(bool(filled[y,x])!=bool(label) for (x,y),label in zip(points,labels));options.append((violations,-float(scores[j]),j,filled))
 _,_,j,mask=min(options,key=lambda x:x[:3]);head=Image.composite(full,Image.new('RGBA',full.size),Image.fromarray(mask.astype('uint8')*255));body=Image.composite(Image.new('RGBA',full.size),full,Image.fromarray(mask.astype('uint8')*255));a=np.array(full);b=np.array(Image.alpha_composite(body,head));assert np.array_equal(a[:,:,3],b[:,:,3])and np.array_equal(a[a[:,:,3]>0],b[a[:,:,3]>0]);head.save(out/f'head-{i:02}.png');body.save(out/f'body-{i:02}.png');Image.fromarray(mask.astype('uint8')*255).save(out/f'mask-{i:02}.png')
 tile=Image.new('RGBA',full.size,'#343941');tile.alpha_composite(head);tile=tile.crop((0,top-8,281,top+172));x=i%4*281;y=i//4*210;board.paste(tile,(x,y+25));draw.text((x+5,y+5),f'{i:02} / candidate{j} / point errors {options[j][0]}',fill='white')
 rows.append({'index':i,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'box':box,'points':points,'labels':labels,'scores':scores.tolist(),'selected_mask':j,'selected_prompt_violations':options[j][0],'hole_fill':True,'visible_recomposition_exact':True,'seconds':time.time()-t});print(i,j,options[j][0],flush=True)
board.save(out/'heads.jpg');(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
