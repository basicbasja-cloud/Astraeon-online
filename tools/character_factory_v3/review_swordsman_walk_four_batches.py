"""Review four 2x2 Walk paint batches at a shared fixed grid, not per-frame fit."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-four-batches-20261104'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 paths=[S/f'batch-{i}.png' for i in range(4)]+[S/f'walk-guide-batch-{i}-20261104.png' for i in range(4)]
 sheets=[]
 for p in paths:
  with Image.open(p) as im:
   if im.width!=im.height:raise ValueError('expected square sheet')
   sheets.append(im.convert('RGB').resize((768,768),Image.Resampling.LANCZOS))
 out.mkdir(parents=True); frames=[]; stats=[]
 for i in range(16):
  j=i%4;x=j%2*384;y=j//2*384;paint=sheets[i//4].crop((x,y,x+384,y+384));guide=sheets[4+i//4].crop((x,y,x+384,y+384));board=Image.new('RGB',(768,410),'white');board.paste(guide,(0,26));board.paste(paint,(384,26));d=ImageDraw.Draw(board);d.text((4,5),f'Guide {i:02}',fill='black');d.text((388,5),f'Batch draft {i:02}',fill='black');frames.append(board)
  a=np.asarray(paint); fg=(a.min(axis=2)<230);yy,xx=np.where(fg)
  if not len(xx):raise ValueError('empty paint frame')
  stats.append({'frame':i,'foreground_bbox':[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1]})
 for name,ms in [('normal.gif',85),('slow.gif',200)]:frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=ms,loop=0,optimize=False)
 for i in (0,3,4,7,8,11,12,15):frames[i].save(out/f'frame{i:02}.png')
 (out/'receipt.json').write_text(json.dumps({'status':'FOUR_BATCH_DRAFT_NOT_ACCEPTED','input_sha256':{p.name:sha(p) for p in paths},'implementation_sha256':sha(Path(__file__)),'frame_stats':stats,'limitations':['Bounding boxes include weapon and costume; no anatomical landmark, foot-contact or size approval.','Separate batches may drift at their seams; no frame-specific fitting is used.','Background is not extracted; no part segmentation, seven views, variants or gameplay.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
