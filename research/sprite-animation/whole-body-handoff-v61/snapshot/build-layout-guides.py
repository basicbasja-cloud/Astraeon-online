from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
root=Path.cwd();out=root/'work/all-actions-v61/generation';seed=Image.open(root/'research/sprite-animation/core-family-v56/frames/idle/S/00.png').convert('RGBA');seed=seed.resize((410,461),Image.Resampling.LANCZOS)
# Uniform seed bank display transform .8, x=-13,y=80. This is a GUIDE only.
# All 8 cells identical registration. No final pose art is being warped.
seedcell=Image.new('RGBA',(384,512));seedcell.alpha_composite(seed,(-13,80))
source=root/'research/sprite-animation/pickup-views-v55/source/S'
for name,indices in [('down',list(range(8))),('up',list(range(8,16)))]:
 template=Image.new('RGBA',(1536,1024));guides=Image.new('RGBA',(1536,1024));dt=ImageDraw.Draw(template);dg=ImageDraw.Draw(guides)
 for slot,i in enumerate(indices):
  x=slot%4*384;y=slot//4*512;template.alpha_composite(seedcell,(x,y));im=Image.open(source/f'{i:02}.png').convert('RGBA');im=im.resize((278,371),Image.Resampling.LANCZOS);guidecell=Image.new('RGBA',(384,512));guidecell.alpha_composite(im,(53,125));guides.alpha_composite(guidecell,(x,y))
  for d in [dt,dg]:
   d.rectangle((x+2,y+2,x+381,y+509),outline=(0,170,255,255),width=2);d.text((x+12,y+10),f'{i:02}',fill=(0,170,255,255));d.line((x+12,y+476,x+100,y+476),fill=(0,170,255,255),width=2);d.line((x+284,y+476,x+371,y+476),fill=(0,170,255,255),width=2)
 template.save(out/f'S-{name}-layout.png');guides.save(out/f'S-{name}-poses.png')
print('Two8slot guides, source-only shared transforms, fixed .8seed and .724source displays')
