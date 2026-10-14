"""One source-display matrix for both kinds of actual 3D captures, all64views.
These are SOURCE PROOFS, not final character sprite art or generated video.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).resolve().parent;s=json.loads((P/'source/source.json').read_text());m=json.loads((P/'guide-bind.json').read_text())['whole_bank_matrix'];scale,tx,ty=m[0],m[4],m[5];inverse=(1/scale,0,-tx/scale,0,1/scale,-ty/scale)
for raw,preview,label in [('source','review-source','ANALYTIC SOURCE'),('hinge-skin-proof','review-skin','HINGE ARM SKIN / SOURCE ONLY')]:
 for v in s['cameras']:
  folder=P/preview/v;folder.mkdir(parents=True,exist_ok=True);ims=[]
  for i in range(8):
   im=Image.open(P/f'{raw}/{v}/{i:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC);im.save(folder/f'{i:02}.png');bg=Image.new('RGBA',im.size,(37,43,51,255));bg.alpha_composite(im);ims.append(bg.convert('RGB'))
  for name,ds in [('source',[190,180,190,180,190,180,190,600]),('game',[100]*7+[600])]:ims[0].save(folder/f'{name}.gif',save_all=True,append_images=ims[1:],duration=ds,loop=0,disposal=2)
 ims=[]
 for i in range(8):
  sheet=Image.new('RGBA',(1536,1024),(37,43,51,255));d=ImageDraw.Draw(sheet)
  for j,v in enumerate(s['cameras']):
   sheet.alpha_composite(Image.open(P/f'{preview}/{v}/{i:02}.png'),(j%4*384,j//4*512));d.text((j%4*384+8,j//4*512+8),v+' / '+label+' / '+str(i+1),fill='white')
  ims.append(sheet.convert('RGB'))
 ims[0].save(P/('eight-view-source-only.gif' if raw=='source' else 'eight-view-skinned-arm-source-only.gif'),save_all=True,append_images=ims[1:],duration=[190,180,190,180,190,180,190,600],loop=0,disposal=2)
print('Both source families: actual64captures, same display matrix and accepted clocks')
