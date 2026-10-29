"""Overlay sampled source skin points on guide and four unapproved Walk masters."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2'
FRAMES=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-walk-sw-fourframe-candidate-20261029/frames'

def build(projection,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 data=json.loads(projection.read_text());guide=json.loads((GUIDE/'manifest.json').read_text())
 if data.get('status')!='SOURCE_SKIN_POINT_PROJECTION_NOT_CONTACT_APPROVAL' or data['guide_sha256']!=hashlib.sha256((GUIDE/'manifest.json').read_bytes()).hexdigest():raise ValueError('projection source mismatch')
 out.mkdir(parents=True);panels=[]
 for i in range(4):
  with Image.open(GUIDE/'SW'/f'{i:03}.png') as im:
   im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);g=bg.crop((420,520,1116,1216)).resize((887,887),Image.Resampling.LANCZOS).convert('RGB')
  with Image.open(FRAMES/f'{i:03}.png') as im:art=im.convert('RGB')
  panel=Image.new('RGB',(768,420),'white');d=ImageDraw.Draw(panel)
  for k,(label,im) in enumerate((('guide',g),('draft',art))):
   draw=ImageDraw.Draw(im)
   for side,color in (('l','#00aaff'),('r','#ff9a00')):
    x,y=data['frames'][i]['feet'][side]['source_guide_xy'];x=(x-420)*887/696;y=(y-520)*887/696;draw.ellipse((x-9,y-9,x+9,y+9),outline=color,width=5);draw.text((x+10,y-16),side,fill=color)
   panel.paste(im.resize((384,384),Image.Resampling.LANCZOS),(k*384,36));d.text((k*384+4,5),f'{label} {i:02}: selected source vertices',fill='black')
  panel.save(out/f'frame{i:02}.png');panels.append(panel)
 panels[0].save(out/'partial-skin-points.gif',save_all=True,append_images=panels[1:],duration=220,loop=0,optimize=False)
 result={'status':'SOURCE_SKIN_OVERLAY_NOT_CONTACT_APPROVAL','projection_sha256':hashlib.sha256(projection.read_bytes()).hexdigest(),
         'limitations':['Source skin point selection changes between poses and is not a verified painted sole.', 'Overlay does not measure gameplay contact, camera scaling, floor or animation quality.', 'Four frames repeated for review, not a walk loop.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--projection',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.projection,a.output)))
