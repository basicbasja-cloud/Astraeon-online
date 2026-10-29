"""Three SAM2 head-mask suggestions for one saved Swordsman paint frame.

Masks are unapproved; SAM output is never used to overwrite source pixels.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw08-single-20261029/generated.png'
CHECKPOINT_SHA='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69'
CROP=(690,590,930,800);BOX=(750,620,900,770);POINTS=((820,680),(785,735),(770,705),(735,700));LABELS=(1,1,1,0)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def build(checkpoint,out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 if sha(checkpoint)!=CHECKPOINT_SHA:raise ValueError('Unexpected SAM2 checkpoint')
 import torch
 from sam2.build_sam import build_sam2
 from sam2.sam2_image_predictor import SAM2ImagePredictor
 torch.set_num_threads(3)
 image=Image.open(SOURCE).convert('RGB')
 if image.size!=(1254,1254):raise ValueError('Unexpected source canvas')
 predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False))
 predictor.set_image(np.asarray(image.crop(CROP)))
 points=np.asarray(POINTS,dtype=float)-np.asarray(CROP[:2]);box=np.asarray(BOX,dtype=float)-np.asarray(CROP[:2]*2)
 masks,scores,_=predictor.predict(point_coords=points,point_labels=np.asarray(LABELS),box=box,multimask_output=True)
 out.mkdir(parents=True);(out/'masks').mkdir();board=Image.new('RGB',(960,320),'#808080');draw=ImageDraw.Draw(board);items=[]
 for i,(local,score) in enumerate(zip(masks,scores)):
  full=np.zeros((1254,1254),np.uint8);full[CROP[1]:CROP[3],CROP[0]:CROP[2]]=local.astype(np.uint8)*255;Image.fromarray(full,'L').save(out/'masks'/f'{i}.png')
  selected=np.asarray(image).copy();alpha=full;selected[alpha==0]=0;layer=Image.fromarray(np.dstack((selected,alpha)),'RGBA');bg=Image.new('RGBA',(240,210),'#808080');bg.alpha_composite(layer.crop(CROP));board.paste(bg.convert('RGB').resize((320,280),Image.Resampling.LANCZOS),(i*320,40));draw.text((i*320+4,5),f'proposal {i} score {float(score):.3f}',fill='black')
  items.append({'index':i,'score':float(score),'mask_pixels':int(np.count_nonzero(local)),'seeds_in_mask':[bool(local[int(y),int(x)])for x,y in points]})
 board.save(out/'proposals.png');proof={'status':'SAM2_HEAD_MASK_CANDIDATES_REQUIRE_SEMANTIC_REVIEW','source_sha256':sha(SOURCE),'checkpoint_sha256':sha(checkpoint),'model_config':'configs/sam2.1/sam2.1_hiera_t.yaml','device':'cpu','crop_source_px':CROP,'head_box_source_px':BOX,'point_coords_source_px':POINTS,'point_labels':LABELS,'proposals':items,'source_modified':False,'runtime_admitted':False,'limitations':['Scores and positive seeds do not certify separation of head from scarf or body.','Masks are suggestions; background alpha, weapon, hidden surfaces and other frames remain unverified.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.checkpoint,a.output)))
