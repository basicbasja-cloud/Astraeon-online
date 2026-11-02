"""Propose head ownership on the same NW003 sword-free master; no intake."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw003-alt-head-20261102/raw.png'
SHA='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(checkpoint,out):
 if out.exists() or out.is_symlink():raise ValueError('use a fresh output')
 if sha(checkpoint)!=SHA:raise ValueError('checkpoint mismatch')
 import torch
 from sam2.build_sam import build_sam2
 from sam2.sam2_image_predictor import SAM2ImagePredictor
 torch.set_num_threads(3)
 with Image.open(SRC) as im:
  rgba=im.convert('RGBA').resize((512,512),Image.Resampling.LANCZOS);bg=Image.new('RGBA',rgba.size,'#888');bg.alpha_composite(rgba);rgb=np.array(bg.convert('RGB'))
 predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False));predictor.set_image(rgb)
 points=np.array([[207,145],[225,195],[291,200],[205,260]],float);labels=np.array([1,1,0,0]);masks,scores,_=predictor.predict(point_coords=points,point_labels=labels,multimask_output=True)
 out.mkdir(parents=True);board=Image.new('RGB',(1200,420),'#777');draw=ImageDraw.Draw(board);items=[]
 for i,(m,score) in enumerate(zip(masks,scores)):
  m = (np.asarray(m) > 0) & (np.asarray(rgba)[:,:,3]>0);Image.fromarray((m*255).astype('uint8')).save(out/f'mask-{i}.png');pixels=np.asarray(rgba).copy();pixels[~m]=0;h=Image.fromarray(pixels,'RGBA');h.save(out/f'head-{i}.png');canvas=Image.new('RGBA',(512,512),'#777');canvas.alpha_composite(h);board.paste(canvas.crop((130,80,310,260)).resize((400,300),Image.Resampling.NEAREST).convert('RGB'),(400*i,40));draw.text((400*i+3,5),f'candidate {i} score {score:.3f}',fill='white');items.append({'index':i,'score':float(score),'pixels':int(m.sum())})
 board.save(out/'proposals.png');proof={'status':'ALTERNATE_HEAD_SEGMENTATION_NOT_APPROVED','source_sha256':sha(SRC),'checkpoint_sha256':sha(checkpoint),'script_sha256':sha(Path(__file__)),'points':points.tolist(),'labels':labels.tolist(),'proposals':items,'limitations':['SAM masks can include arm, scarf or omit face/neck; scores do not establish semantic ownership.','Underpainting, hilt, alpha edges, other frames, asset swaps and gameplay remain unapproved.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(run(a.checkpoint,a.output)))
