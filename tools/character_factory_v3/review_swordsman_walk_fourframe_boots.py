"""Compare four full-body SW Walk proposals with projected source foot points."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
OLD=BASE/'review/swordsman-walk-sw-fourframe-candidate-20261029/frames'
NEW02=BASE/'review/swordsman-walk-sw02-sole-crop-20261029'
NEW03=BASE/'review/swordsman-walk-sw03-sole-crop-20261029'
PROJECTION=BASE/'research/swordsman-walk-feet-projection-20261029/receipt.json'
GUIDE=BASE/'guides/4e519e1eadc69aaf28a2'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 checks=[(NEW02/'receipt.json',OLD/'002.png'),(NEW03/'receipt.json',OLD/'003.png')]
 for receipt,source in checks:
  x=json.loads(receipt.read_text())
  if x.get('source_sha256',x.get('records',[{}])[0].get('input_sha256'))!=sha(source):raise ValueError('stale correction source')
 projection=json.loads(PROJECTION.read_text());frames=[];records=[];out.mkdir(parents=True);(out/'frames').mkdir()
 for i in range(4):
  path=OLD/f'{i:03}.png' if i<2 else NEW02/'v2.png' if i==2 else NEW03/'candidate.png'
  with Image.open(path) as im:
   if im.size!=(887,887):raise ValueError('unexpected frame size')
   art=im.convert('RGB')
  art.save(out/'frames'/f'{i:03}.png')
  with Image.open(GUIDE/'SW'/f'{i:03}.png') as im:
   im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);g=bg.crop((420,520,1116,1216)).resize((887,887),Image.Resampling.LANCZOS).convert('RGB')
  board=Image.new('RGB',(768,420),'white');draw=ImageDraw.Draw(board)
  for k,(label,im) in enumerate((('guide',g),('candidate',art.copy()))):
   d=ImageDraw.Draw(im)
   for side,color in (('l','#00aaff'),('r','#ff9a00')):
    x,y=projection['frames'][i]['feet'][side]['source_guide_xy'];x=(x-420)*887/696;y=(y-520)*887/696;d.ellipse((x-10,y-10,x+10,y+10),outline=color,width=5)
   board.paste(im.resize((384,384),Image.Resampling.LANCZOS),(k*384,36));draw.text((k*384+4,6),f'{label} {i:02} / partial',fill='black')
  board.save(out/f'frame{i:02}.png');frames.append(board);records.append({'frame':i,'source':str(path.relative_to(ROOT)),'source_sha256':sha(path)})
 frames[0].save(out/'partial-four-frames.gif',save_all=True,append_images=frames[1:],duration=160,loop=0,optimize=False)
 result={'status':'FOUR_FRAME_BOOT_REPAINT_STUDY_NOT_APPROVED','frames':records,'projection_sha256':sha(PROJECTION),
         'limitations':['Circles are selected source mesh points, not verified painted sole contacts.', 'Head, anatomy, footwear size, temporal stability and game floor remain unverified.', 'Four frames repeated for review, not a complete walk loop or runtime asset.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
