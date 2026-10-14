from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
P=Path(__file__).resolve().parent
s=json.loads((P/'source/source.json').read_text());im=Image.open(P/'source/character/S/00.png').convert('RGBA');a=np.array(im.getchannel('A'));yy,xx=np.where(a>=128);scale=398/(yy.max()-yy.min());tx=192-scale*192;ty=82-scale*yy.min();matrix=[scale,0,0,scale,tx,float(ty)];inverse=[1/scale,0,-tx/scale,0,1/scale,-ty/scale]
for view in s['cameras']:
 atlas=Image.new('RGBA',(1536,1024));folder=P/'guides'/view;folder.mkdir(parents=True,exist_ok=True)
 for i in range(8):
  im=Image.open(P/f'source/{view}/{i:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC);im.save(folder/f'{i:02}.png');atlas.alpha_composite(im,(i%4*384,i//4*512))
 atlas.save(P/f'guide-{view}.png')
(P/'guide-bind.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((P/'source/source.json').read_bytes()).hexdigest(),whole_bank_matrix=matrix,calibration='One ACTOR-ONLY S-neutral height399/floor480 transform shared unchanged by all64rendered views; excludes the separate collectible during calibration. Not per-view bbox fitting or final painted-image normalization.',production_pass=False),indent=2)+'\n')
sheet=Image.new('RGBA',(1536,1024),(35,40,47,255));d=ImageDraw.Draw(sheet)
for j,v in enumerate(s['cameras']):
 sheet.alpha_composite(Image.open(P/f'guides/{v}/03.png'),(j%4*384,j//4*512));d.text((j%4*384+10,j//4*512+10),v,fill='white')
sheet.convert('RGB').save(P/'eight-view-contact-source.png')

owner=json.loads((P/'source-owner-eight/source.json').read_text()) if (P/'source-owner-eight/source.json').exists() else None
if owner:
 for view in s['cameras']:
  atlas=Image.new('RGBA',(1536,1024))
  for i in range(8):
   im=Image.open(P/f'source-owner-eight/{view}/{i:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC);atlas.alpha_composite(im,(i%4*384,i//4*512))
  atlas.save(P/f'guide-{view}-owner.png')
