"""Propose same-frame NW005 head masks; scores are not semantic approval."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW/Master/005.png';CHECKPOINT='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69';POINTS=((270,201),(266,217),(252,200),(248,197),(270,238),(230,150));LABELS=(1,1,1,0,0,0)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(checkpoint,out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 if sha(checkpoint)!=CHECKPOINT:raise ValueError('checkpoint mismatch')
 import torch
 from sam2.build_sam import build_sam2
 from sam2.sam2_image_predictor import SAM2ImagePredictor
 torch.set_num_threads(3)
 with Image.open(SRC) as im:source=im.convert('RGBA')
 bg=Image.new('RGBA',source.size,'#777');bg.alpha_composite(source);rgb=np.array(bg.convert('RGB'));p=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False));p.set_image(rgb);masks,scores,_=p.predict(point_coords=np.array(POINTS,float),point_labels=np.array(LABELS),multimask_output=True)
 out.mkdir(parents=True);board=Image.new('RGB',(1200,400),'#777');d=ImageDraw.Draw(board);records=[]
 for i,(m,v) in enumerate(zip(masks,scores)):
  m=(np.asarray(m)>0)&(np.asarray(source)[:,:,3]>0);Image.fromarray((m*255).astype('uint8')).save(out/f'mask{i}.png');a=np.array(source);a[~m]=0;bg=Image.new('RGBA',source.size,'#777');bg.alpha_composite(Image.fromarray(a));board.paste(bg.crop((220,170,300,250)).resize((400,400),Image.Resampling.NEAREST).convert('RGB'),(i*400,0));d.text((i*400+3,3),f'{i} score {v:.3f}',fill='white');records.append({'index':i,'score':float(v),'pixels':int(m.sum())})
 board.save(out/'proposals.png');proof={'status':'NW005_HEAD_SAM_NOT_APPROVED','source_sha256':sha(SRC),'checkpoint_sha256':sha(checkpoint),'script_sha256':sha(Path(__file__)),'points':POINTS,'labels':LABELS,'proposals':records,'limitations':['Hair behind the sword is not authored, and SAM can include scarf or metal.', 'One frame only; no swap, animation or game acceptance.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.checkpoint,a.output)))
