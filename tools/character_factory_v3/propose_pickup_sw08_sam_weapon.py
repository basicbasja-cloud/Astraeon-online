"""Suggest SW08 weapon masks with SAM2; no automatic semantic approval."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw08-single-20261029/generated.png'
CHECKPOINT_SHA='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69'
CROP=(560,910,850,1060);BOX=(580,950,820,1040);POINTS=((720,995),(640,1000),(620,935),(760,950));LABELS=(1,1,0,0)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(checkpoint,out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 if sha(checkpoint)!=CHECKPOINT_SHA:raise ValueError('Unexpected SAM2 checkpoint')
 import torch
 from sam2.build_sam import build_sam2
 from sam2.sam2_image_predictor import SAM2ImagePredictor
 torch.set_num_threads(3);image=Image.open(SOURCE).convert('RGB')
 if image.size!=(1254,1254):raise ValueError('Unexpected source canvas')
 predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False));predictor.set_image(np.asarray(image.crop(CROP)))
 points=np.asarray(POINTS,float)-np.asarray(CROP[:2]);box=np.asarray(BOX,float)-np.asarray(CROP[:2]*2);masks,scores,_=predictor.predict(point_coords=points,point_labels=np.asarray(LABELS),box=box,multimask_output=True)
 out.mkdir(parents=True);(out/'masks').mkdir();board=Image.new('RGB',(1160,230),'#808080');draw=ImageDraw.Draw(board);records=[]
 for i,(local,score) in enumerate(zip(masks,scores)):
  full=np.zeros((1254,1254),np.uint8);full[CROP[1]:CROP[3],CROP[0]:CROP[2]]=local.astype(np.uint8)*255;Image.fromarray(full,'L').save(out/'masks'/f'{i}.png');selected=np.asarray(image).copy();selected[full==0]=0;layer=Image.fromarray(np.dstack((selected,full)),'RGBA');bg=Image.new('RGBA',(290,150),'#808080');bg.alpha_composite(layer.crop(CROP));board.paste(bg.convert('RGB').resize((386,200),Image.Resampling.LANCZOS),(i*386,30));draw.text((i*386+4,5),f'candidate {i} score {float(score):.3f}',fill='black');records.append({'index':i,'score':float(score),'pixels':int(np.count_nonzero(local)),'seeds_in_mask':[bool(local[int(y),int(x)])for x,y in points]})
 board.save(out/'proposals.png');proof={'status':'SAM2_WEAPON_MASK_CANDIDATES_NOT_APPROVED','source_sha256':sha(SOURCE),'checkpoint_sha256':sha(checkpoint),'crop':CROP,'box':BOX,'points':POINTS,'labels':LABELS,'proposals':records,'source_modified':False,'runtime_admitted':False,'limitations':['A score does not certify sword/hand/boot boundary or hidden handle.','One frame only; no valid weapon swap or game action.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.checkpoint,a.output)))
