"""Propose one translation per complete frame from an unverified hair proxy."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-adjacent-pairs-20261029'
MASKS=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-sw-pair-head-sam-20261029'
MANIFEST=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2/manifest.json'

def centroid(path):
 with Image.open(path) as im:a=np.asarray(im.convert('L'))>0
 y,x=np.where(a)
 if not x.size:raise ValueError('empty mask')
 return np.array([x.mean(),y.mean()])

def translate(image,delta):
 dx,dy=map(int,delta);a=np.asarray(image.convert('RGB'));fg=np.any(a<245,axis=2);y,x=np.where(fg)
 if x.size==0 or x.min()+dx<0 or x.max()+dx>=image.width or y.min()+dy<0 or y.max()+dy>=image.height:raise ValueError('translation clips foreground')
 result=Image.new('RGB',image.size,'white');result.paste(image,(dx,dy));return result

def make(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 manifest=json.loads(MANIFEST.read_text());frames=manifest['views']['SW']['frames'];masks=[MASKS/f'{i:03}/2.png' for i in range(4)];centers=[centroid(p) for p in masks]
 scale=887/696;guide=[np.array(f['landmarks']['head']) for f in frames[:4]];out.mkdir(parents=True);(out/'frames').mkdir();panels=[];records=[]
 for i in range(4):
  source=P/('paint-00-01.png' if i<2 else 'paint-02-03.png')
  with Image.open(source) as sheet:
   if sheet.size!=(1774,887):raise ValueError('unexpected sheet size')
   image=sheet.convert('RGB').crop(((i%2)*887,0,(i%2+1)*887,887))
  target=(guide[i]-guide[0])*scale;observed=centers[i]-centers[0];delta=np.rint(target-observed).astype(int);proposed=translate(image,delta)
  proposed.save(out/'frames'/f'{i:03}.png');panel=Image.new('RGB',(888,470),'white');panel.paste(image.resize((444,444),Image.Resampling.LANCZOS),(0,26));panel.paste(proposed.resize((444,444),Image.Resampling.LANCZOS),(444,26));d=ImageDraw.Draw(panel);d.text((5,5),f'frame {i:02} original',fill='black');d.text((449,5),f'frame {i:02} proposal; partial sequence',fill='black');panels.append(panel)
  residual=(observed+delta-target)*696/887*240/1536
  records.append({'frame':i,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'mask_sha256':hashlib.sha256(masks[i].read_bytes()).hexdigest(),'translation_source_tile_px':delta.tolist(),'head_proxy_residual_from_frame00_runtime_px':residual.tolist()})
 panels[0].save(out/'partial-comparison.gif',save_all=True,append_images=panels[1:],duration=160,loop=0,optimize=False)
 result={'status':'WHOLE_FRAME_REGISTRATION_PROPOSAL_NOT_APPROVED','frames':records,'guide_sha256':hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),'limitations':['SAM hair centroid may omit face, and is not an anatomical head or socket landmark.', 'A shared full-frame shift can improve hair registration while worsening foot contact and weapon position.', 'Only four frames in one direction; the GIF repeats a partial sequence, not a walk loop.', 'No alpha, semantic cutouts, variants, gameplay or runtime admission.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(make(a.output)))
