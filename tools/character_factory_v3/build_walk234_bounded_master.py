"""Bound three same-pose rear-leg paint corrections to fixed review masks."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-baseline-seam-repair-20261104/generated-sheet.png'
JOB=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk234-rearleg-20261104'
POLYGONS={2:[(95,240),(168,233),(199,250),(199,275),(188,297),(178,325),(95,325)],3:[(95,236),(171,233),(199,252),(194,275),(182,297),(175,320),(95,320)],4:[(95,230),(168,226),(192,250),(184,275),(173,297),(165,317),(95,317)]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists():raise ValueError('Choose fresh output')
 base=Image.open(BASE).convert('RGB').resize((1536,1536),Image.Resampling.LANCZOS)
 proposal=Image.open(JOB/'proposal.png').convert('RGB').resize((1536,512),Image.Resampling.LANCZOS)
 result=base.copy();out.mkdir(parents=True);receipt=[]
 for col,i in enumerate((2,3,4)):
  box=(i%4*384,i//4*384,(i%4+1)*384,(i//4+1)*384)
  before=base.crop(box);paint=proposal.crop((col*512,0,(col+1)*512,512)).resize((384,384),Image.Resampling.LANCZOS)
  mask=Image.new('L',(384,384));ImageDraw.Draw(mask).polygon(POLYGONS[i],fill=255)
  after=Image.composite(paint,before,mask);result.paste(after,box[:2])
  a,b,m=np.asarray(before),np.asarray(after),np.asarray(mask)
  changed=int(np.any(a!=b,axis=2)[m==0].sum());assert changed==0
  after.save(out/f'master{i:02}.png');mask.save(out/f'mask{i:02}.png')
  receipt.append({'frame':i,'protected_changed_pixels':changed,'polygon_384':POLYGONS[i]})
 # Exact preservation of every other complete frame.
 untouched=[]
 for i in range(16):
  if i in POLYGONS:continue
  box=(i%4*384,i//4*384,(i%4+1)*384,(i//4+1)*384)
  assert base.crop(box).tobytes()==result.crop(box).tobytes();untouched.append(i)
 result.save(out/'review-sheet.png')
 panels=[]
 for i in range(1,6):
  box=(i%4*384,i//4*384,(i%4+1)*384,(i//4+1)*384)
  p=Image.new('RGB',(768,412),'white');p.paste(base.crop(box),(0,28));p.paste(result.crop(box),(384,28));d=ImageDraw.Draw(p);d.text((4,4),f'original draft {i:02}',fill='black');d.text((388,4),f'bounded draft {i:02}',fill='black');p.save(out/f'compare{i:02}.png');panels.append(p)
 panels[0].save(out/'neighbors.gif',save_all=True,append_images=panels[1:],duration=200,loop=0,optimize=False)
 (out/'receipt.json').write_text(json.dumps({'status':'BOUNDED_THREE_FRAME_DRAFT_NOT_ACCEPTED','base_sha256':sha(BASE),'proposal_sha256':sha(JOB/'proposal.png'),'script_sha256':sha(Path(__file__)),'frames':receipt,'unchanged_frames':untouched,'limitations':['No verified anatomical sole measurements or full animation approval.','Fixed review scale; resizing adds no source detail.','No runtime admission, cutouts or variants.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
