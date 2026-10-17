from pathlib import Path
from PIL import Image,ImageDraw
import json
r=Path.cwd();p=r/'work/all-actions-v61/generation'
for v in ['W','E']:
 seed=Image.open(r/f'research/sprite-animation/core-family-v56/frames/idle/{v}/00.png').convert('RGBA').resize((410,461),Image.Resampling.LANCZOS)
 bank=Image.new('RGBA',(1536,1024));guide=Image.new('RGBA',(1536,1024));d=ImageDraw.Draw(bank);dg=ImageDraw.Draw(guide)
 for i in range(8):
  x=i%4*384;y=i//4*512;bank.alpha_composite(seed,(x-13,y+80))
  f=r/f'research/sprite-animation/pickup-views-v55/source/{v}/{i:02}.png'
  if f.exists():
   im=Image.open(f).convert('RGBA').resize((278,371),Image.Resampling.LANCZOS);guide.alpha_composite(im,(x+53,y+125))
  for draw in [d,dg]:
   draw.rectangle((x+2,y+2,x+381,y+509),outline=(0,170,255,255),width=2);draw.text((x+12,y+10),f'{v} {i:02}',fill=(0,170,255,255));draw.line((x+12,y+476,x+100,y+476),fill=(0,170,255,255),width=2);draw.line((x+284,y+476,x+371,y+476),fill=(0,170,255,255),width=2)
 bank.save(p/f'{v}-pickup-layout.png');guide.save(p/f'{v}-pickup-poses-guide.png')
