"""Review eight nonadjacent poses, never use them as an animation."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-skill-sw-keyposes-20261029'
POSES = (0, 4, 8, 12, 16, 20, 24, 31)

def bounds(image):
 a = np.asarray(image.convert('RGB'))
 foreground = np.min(a, axis=2) < 230
 foreground[:24, :35] = False  # Exclude source-sheet labels only.
 y, x = np.where(foreground)
 if x.size == 0: raise ValueError('empty tile')
 return [int(x.min()), int(y.min()), int(x.max()) + 1, int(y.max()) + 1]

def build(out):
 if out.exists() or out.is_symlink(): raise ValueError('choose fresh output')
 paths = [P/'guide.png', P/'generated.png']
 sheets = []
 for p in paths:
  with Image.open(p) as im: sheets.append(im.convert('RGB').resize((1536,768),Image.Resampling.LANCZOS))
 out.mkdir(parents=True)
 frames=[]; measures=[]
 for j, pose in enumerate(POSES):
  x,y=(j%4)*384,(j//4)*384
  tiles=[s.crop((x,y,x+384,y+384)) for s in sheets]
  panel=Image.new('RGB',(768,416),'white'); panel.paste(tiles[0],(0,32)); panel.paste(tiles[1],(384,32))
  d=ImageDraw.Draw(panel);d.text((5,7),f'GUIDE pose {pose:02} / 32',fill='black');d.text((389,7),f'DRAFT pose {pose:02} / NOT ANIMATION',fill='black');frames.append(panel)
  measures.append({'pose':pose,'guide_bbox':bounds(tiles[0]),'draft_bbox':bounds(tiles[1])})
 frames[0].save(out/'keypose-comparison.gif',save_all=True,append_images=frames[1:],duration=1250,loop=0,optimize=False)
 result={'status':'DRAFT_NOT_ACCEPTED','poses':list(POSES),'measurements':measures,'inputs_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'limitations':['Only eight nonadjacent images out of 32 SW frames.','Foreground bounds include hair, clothing and sword; they are not anatomical landmarks. Source labels are excluded in the top-left 35x24 pixels.','Paint may have changed anatomy, registration, sword and costume; no motion, cutouts or runtime certification.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
