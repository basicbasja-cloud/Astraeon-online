"""One clean neutral calibration for the whole source family, never per-pose fitting."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;src=P/'source/neutral-calibration-S.png';a=np.array(Image.open(src));y,x=np.where(a[:,:,3]>=128);assert x.min()>0 and y.min()>0 and x.max()<383 and y.max()<511;s=398/(y.max()-y.min());tx=224-192*s;ty=490-y.max()*s
for view in ['S','SW','W','NW','N','NE','E','SE']:
 for mode in ['full','leg-owner']:
  out=Image.new('RGB',(1536,1024),(40,43,48));d=ImageDraw.Draw(out)
  for i in range(8):
   im=Image.open(P/f'guides/{view}/{mode}/{i:02}.png');im=im.transform((384,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC);out.paste(im,(i%4*384,i//4*512),im);d.text((i%4*384+5,i//4*512+5),f'{view} {i}',fill='white')
  out.save(P/f'guides/{view}/{mode}-registered-eight.png')
(P/'source/guide-display-affine.json').write_text(json.dumps({'scale':float(s),'translation':[float(tx),float(ty)],'calibration_source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'neutral_alpha128_bbox':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'calibration':'Single prop-free neutral S guide alpha128 height to399px; same affine all physical views and all walk phases, never fitting painted art','production_pass':False},indent=2)+'\n');print(s,tx,ty)
