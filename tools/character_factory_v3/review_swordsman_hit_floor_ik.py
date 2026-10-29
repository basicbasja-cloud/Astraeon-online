"""Compare an IK study with the same uncorrected guide; no runtime approval."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
DIRECTIONS=('S','SW','W','NW','N','NE','E','SE')

def make(baseline,candidate,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 old=json.loads((baseline/'manifest.json').read_text());new=json.loads((candidate/'manifest.json').read_text());diag=json.loads((candidate/'floor-ik-diagnostic.json').read_text())
 if old['frame_count']!=20 or new['frame_count']!=20 or not new['job'].get('floor_ik_experiment') or set(new['views'])!=set(DIRECTIONS):raise ValueError('unexpected guide study')
 unchanged=[]
 for i in list(range(12))+[19]:
  with Image.open(baseline/'SW'/f'{i:03}.png') as a, Image.open(candidate/'SW'/f'{i:03}.png') as b:
   unchanged.append({'frame':i,'rgba_equal':ImageChops.difference(a.convert('RGBA'),b.convert('RGBA')).getbbox() is None})
 out.mkdir(parents=True);pairs=[];grids=[]
 for i in range(20):
  pair=Image.new('RGB',(736,438),'white');d=ImageDraw.Draw(pair)
  for k,(folder,label) in enumerate(((baseline,'baseline'),(candidate,'IK candidate'))):
   with Image.open(folder/'SW'/f'{i:03}.png') as im:
    if im.size!=(768,768):raise ValueError('unexpected guide size')
    im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);pair.paste(bg.crop((200,200,568,608)).convert('RGB'),(k*368,30));d.text((k*368+4,5),f'{label} SW {i:02}',fill='black')
  pairs.append(pair)
  grid=Image.new('RGB',(768,416),'white');d=ImageDraw.Draw(grid)
  for k,direction in enumerate(DIRECTIONS):
   with Image.open(candidate/direction/f'{i:03}.png') as im:
    im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);x=k%4*192;y=k//4*208;grid.paste(bg.crop((224,260,544,600)).resize((192,192),Image.Resampling.LANCZOS).convert('RGB'),(x,y+16));d.text((x+4,y+1),f'{direction} {i:02}',fill='black')
  grids.append(grid)
 for name,frames in [('sw-comparison.gif',pairs),('eight-views.gif',grids)]:frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=[80]*19+[400],loop=0,optimize=False)
 pairs[15].save(out/'sw-frame15.png')
 result={'status':'FLOOR_IK_SOURCE_STUDY_NOT_APPROVED','baseline_manifest_sha256':hashlib.sha256((baseline/'manifest.json').read_bytes()).hexdigest(),'candidate_manifest_sha256':hashlib.sha256((candidate/'manifest.json').read_bytes()).hexdigest(),
         'diagnostic_sha256':hashlib.sha256((candidate/'floor-ik-diagnostic.json').read_bytes()).hexdigest(),'sw_unchanged_frames':unchanged,
         'limitations':['Floor minima use foot/ball skin weights, not verified planted soles.',
                        'No between-sample collision, gameplay floor, knee anatomy, sword volume, or painted master acceptance.',
                        'GIF repeats one-shot with illustrative timing, not proof of runtime transition.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(make(a.baseline,a.candidate,a.output)))
