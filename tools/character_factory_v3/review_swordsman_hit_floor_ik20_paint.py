"""Compare a provisional 20-pose Hit-to-Idle draft with its locked guide."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-hit-sw-floor-ik20-20261103'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(output):
 if output.exists() or output.is_symlink():raise ValueError('choose fresh output')
 paths=[S/'guide.png',S/'paint.png']; sheets=[]
 for p in paths:
  with Image.open(p) as im:
   if abs(im.width/im.height-1.25)>.01:raise ValueError('sheet is not approximately 5:4')
   sheets.append(im.convert('RGB').resize((1600,1280),Image.Resampling.LANCZOS))
 frames=[]
 for i in range(20):
  x=i%5*320;y=i//5*320;b=Image.new('RGB',(640,344),'white');d=ImageDraw.Draw(b)
  for j,s in enumerate(sheets):b.paste(s.crop((x,y,x+320,y+320)),(j*320,24));d.text((j*320+4,4),f'{"guide" if j==0 else "paint draft"} {i:02}',fill='black')
  frames.append(b)
 output.mkdir(parents=True)
 for name,ms in (('normal.gif',100),('slow.gif',220)):frames[0].save(output/name,save_all=True,append_images=frames[1:],duration=[ms]*19+[ms*5],loop=0,optimize=False)
 for i in (0,6,11,15,19):frames[i].save(output/f'frame{i:02}.png')
 (output/'receipt.json').write_text(json.dumps({'status':'DRAFT_NOT_APPROVED','frames':20,'input_sha256':{p.name:sha(p) for p in paths},'script_sha256':sha(Path(__file__)),'limitations':['Preview timing and loop are diagnostic only, not gameplay behavior.','Only SW direction; paint anatomy, contact, grip and transition remain unapproved.','White sheet is not a layered authoring master; effective per-slot resolution is low.','No cutouts, variants, gameplay or source-generation seed.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
