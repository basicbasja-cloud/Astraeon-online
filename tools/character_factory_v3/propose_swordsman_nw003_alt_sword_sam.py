"""Propose alternate-sword masks; suggestions require semantic review."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw003-sword-variant-20261030/raw.png'
CHECKPOINT_SHA='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69'
POINTS=((420,741),(565,648),(710,555),(844,470),(386,760),(520,780),(600,510),(780,590),(250,845));LABELS=(1,1,1,1,1,0,0,0,0)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(checkpoint,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 if sha(checkpoint)!=CHECKPOINT_SHA:raise ValueError('unexpected checkpoint')
 import torch
 from sam2.build_sam import build_sam2
 from sam2.sam2_image_predictor import SAM2ImagePredictor
 torch.set_num_threads(3)
 with Image.open(SOURCE) as im:image=im.convert('RGB')
 if image.size!=(1254,1254):raise ValueError('unexpected canvas')
 predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False));predictor.set_image(np.asarray(image))
 masks,scores,_=predictor.predict(point_coords=np.array(POINTS,float),point_labels=np.array(LABELS),multimask_output=True)
 out.mkdir(parents=True);board=Image.new('RGB',(1200,450),'#777');draw=ImageDraw.Draw(board);records=[]
 for i,(mask,score) in enumerate(zip(masks,scores)):
  alpha=(mask.astype('uint8')*255);Image.fromarray(alpha,'L').save(out/f'mask-{i}.png');layer=Image.fromarray(np.dstack((np.asarray(image),alpha)),'RGBA');layer.save(out/f'weapon-{i}.png')
  bg=Image.new('RGBA',image.size,'#777');bg.alpha_composite(layer);board.paste(bg.crop((80,300,1020,1040)).resize((400,315),Image.Resampling.LANCZOS).convert('RGB'),(400*i,55));draw.text((400*i+3,5),f'proposal {i} SAM score {float(score):.3f}',fill='white')
  records.append({'index':i,'score':float(score),'pixels':int(mask.sum()),'seeds':[bool(mask[y,x]) for x,y in POINTS]})
 board.save(out/'proposals.png');proof={'status':'UNAPPROVED_ALTERNATE_WEAPON_SEGMENTATION','source_sha256':sha(SOURCE),'checkpoint_sha256':sha(checkpoint),'script_sha256':sha(Path(__file__)),'points':POINTS,'labels':LABELS,'records':records,'limitations':['SAM binary masks are suggestions and can include glove, background or garment; scores are not semantic approval.', 'Generated sword position, scale and hand grip must be inspected against locked master.', 'Original alpha, other frames, occlusion, variants and gameplay remain unverified.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.checkpoint,a.output)))
