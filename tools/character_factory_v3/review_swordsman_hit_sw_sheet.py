"""Review the unapproved 12-frame SW Hit draft with a fixed square source crop."""
import argparse,hashlib,json
import numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-hit-sw-wholesheet-20261029'
CROP=(448,520,1088,1160)

def square_crop(box):
 if box[2]-box[0]!=box[3]-box[1] or box[2]<=box[0]:raise ValueError('crop must be a nonempty square')
 return box

def guide(source,output):
 if output.exists() or output.is_symlink():raise ValueError('choose fresh output')
 box=square_crop(CROP);board=Image.new('RGB',(1536,1152),'white')
 for i in range(12):
  with Image.open(source/'SW'/f'{i:03}.png') as im:
   if im.size!=(1536,1536):raise ValueError('expected 1536 source')
   im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
   alpha=im.getchannel('A');bbox=alpha.getbbox()
   if bbox is None or bbox[0]<box[0] or bbox[1]<box[1] or bbox[2]>box[2] or bbox[3]>box[3]:raise ValueError(f'guide clipped at frame {i}')
   board.paste(bg.crop(box).resize((384,384),Image.Resampling.LANCZOS).convert('RGB'),((i%4)*384,(i//4)*384))
 board.save(output)

def review(output):
 if output.exists() or output.is_symlink():raise ValueError('choose fresh output')
 paths=[P/'square-guide.png',P/'square-paint.png'];sheets=[]
 for path in paths:
  with Image.open(path) as im:
   if im.width*3!=im.height*4:raise ValueError('expected exact 4:3 sheet aspect')
   sheets.append(im.convert('RGB').resize((1536,1152),Image.Resampling.LANCZOS))
 a=[np.asarray(sheet.crop((0,0,384,384)),dtype=np.int16) for sheet in sheets]
 b=[np.asarray(sheet.crop((1152,768,1536,1152)),dtype=np.int16) for sheet in sheets]
 seam=[]
 for left,right in zip(a,b):
  fg=(left.min(axis=2)<230)|(right.min(axis=2)<230)
  if not fg.any():raise ValueError('empty source pose')
  seam.append({'union_pixels':int(fg.sum()),'mean_rgb_delta_in_union':float(np.abs(left-right).mean(axis=2)[fg].mean()),'different_pixels_in_union':int((np.any(left!=right,axis=2)&fg).sum())})
 output.mkdir(parents=True);frames=[]
 for i in range(12):
  x=(i%4)*384;y=(i//4)*384;canvas=Image.new('RGB',(768,416),'white')
  for k,sheet in enumerate(sheets):canvas.paste(sheet.crop((x,y,x+384,y+384)),(k*384,32))
  d=ImageDraw.Draw(canvas);d.text((4,6),f'GUIDE SW HIT {i:02}',fill='black');d.text((388,6),f'PAINT DRAFT SW HIT {i:02}',fill='black');frames.append(canvas)
 for name,duration in [('normal.gif',100),('slow.gif',220)]:frames[0].save(output/name,save_all=True,append_images=frames[1:],duration=[duration]*11+[duration*4],loop=0,optimize=False)
 for i in (0,3,7,10,11):frames[i].save(output/f'frame{i:02}.png')
 receipt={'status':'DRAFT_NOT_APPROVED','source_crop':list(CROP),'frames':12,'same_source_pose_00_vs_11_foreground_difference':seam,'whole_sheet_resize':[1536,1152],'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'limitations':['One SW view; seven other Hit directions missing.','Generated sheet is not 768px of per-frame artwork and white background has not been extracted.','Review GIF repeats a one-shot for inspection; timing and transition are not gameplay validation.','Foreground comparison includes costume, sword and shading and is not a landmark or one-shot transition acceptance.', 'No anatomy/contact, grip, layer, variant or runtime acceptance.']}
 (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True);g=sub.add_parser('guide');g.add_argument('--source',type=Path,required=True);g.add_argument('--output',type=Path,required=True);r=sub.add_parser('review');r.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.command=='guide':guide(a.source,a.output)
 else:print(json.dumps(review(a.output)))
