"""Propose SAM2 head masks for four adjacent unapproved walk frames."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-adjacent-pairs-20261029'
CHECKPOINT='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69'
CROP=(350,120,600,300);BOX=(400,140,565,270);POINTS=((470,185),(470,220),(370,220));LABELS=(1,1,0)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists() or a.output.is_symlink():raise ValueError('Choose fresh output')
 if sha(a.checkpoint)!=CHECKPOINT:raise ValueError('Unexpected SAM checkpoint')
 import torch
 from sam2.build_sam import build_sam2
 from sam2.sam2_image_predictor import SAM2ImagePredictor
 torch.set_num_threads(3);predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(a.checkpoint),device='cpu',apply_postprocessing=False))
 a.output.mkdir(parents=True);board=Image.new('RGB',(960,960),'#808080');d=ImageDraw.Draw(board);records=[]
 for i in range(4):
  path=P/('paint-00-01.png' if i<2 else 'paint-02-03.png')
  with Image.open(path) as sheet:
   if sheet.size!=(1774,887):raise ValueError('unexpected pair geometry')
   image=sheet.convert('RGB').crop(((i%2)*887,0,(i%2+1)*887,887))
  predictor.set_image(np.array(image.crop(CROP),copy=True));points=np.asarray(POINTS,dtype=float)-np.asarray(CROP[:2]);box=np.asarray(BOX,dtype=float)-np.asarray(CROP[:2]*2)
  masks,scores,_=predictor.predict(point_coords=points,point_labels=np.asarray(LABELS),box=box,multimask_output=True)
  folder=a.output/f'{i:03}';folder.mkdir();items=[]
  for k,(m,score) in enumerate(zip(masks,scores)):
   full=np.zeros((887,887),dtype=np.uint8);full[CROP[1]:CROP[3],CROP[0]:CROP[2]]=m.astype(np.uint8)*255;Image.fromarray(full,'L').save(folder/f'{k}.png')
   rgba=np.dstack((np.asarray(image),full));layer=Image.fromarray(rgba,'RGBA');bg=Image.new('RGBA',(250,180),'#808080');bg.alpha_composite(layer.crop(CROP));board.paste(bg.convert('RGB').resize((320,210),Image.Resampling.LANCZOS),(k*320,i*240+25));d.text((k*320+4,i*240+4),f'frame {i:02} mask {k}',fill='black')
   y,x=np.where(full>0);items.append({'mask':k,'score':float(score),'area':len(x),'centroid':[float(x.mean()),float(y.mean())] if len(x) else None,'seeds_in_mask':[bool(m[int(y),int(x)]) for x,y in points]})
  records.append({'frame':i,'sheet':path.name,'sheet_sha256':sha(path),'proposals':items})
 board.save(a.output/'proposals.png');receipt={'status':'HEAD_PROPOSALS_REQUIRE_SEMANTIC_REVIEW','checkpoint_sha256':CHECKPOINT,'source_crop':list(CROP),'head_box':list(BOX),'positive_negative_points':POINTS,'labels':LABELS,'records':records,'limitations':['Masks can include scarf or omit facial features; centroid is not an anatomical landmark.', 'Four frames of one view; no full walk, floor contact, alpha, cutout, or runtime approval.']};(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
