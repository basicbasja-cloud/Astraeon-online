from PIL import Image,ImageDraw
from pathlib import Path
import json
r=Path.cwd();p=r/'work/all-actions-v61/generation';views=['S','SW','W','NW','N','NE','E','SE']
for v in views:
 bank=Image.new('RGBA',(1536,1024));guide=Image.new('RGBA',bank.size);d=ImageDraw.Draw(bank);dg=ImageDraw.Draw(guide)
 for i in range(8):
  x=i%4*384;y=i//4*512
  for a,sheet,n in [('idle',bank,0),('walk',guide,i*10)]:
   im=Image.open(r/f'research/sprite-animation/core-family-v56/frames/{a}/{v}/{n:02}.png').convert('RGBA').resize((410,461),Image.Resampling.LANCZOS);sheet.alpha_composite(im,(x-13,y+80))
  for dr in [d,dg]:dr.rectangle((x+2,y+2,x+381,y+509),outline=(0,170,255,255),width=2);dr.text((x+12,y+10),f'{v} GAIT PHASE {i}',fill=(0,170,255,255));dr.line((x+12,y+476,x+75,y+476),fill=(0,170,255,255),width=1)
 bank.save(p/f'{v}-walk-layout.png');guide.save(p/f'{v}-walk-poses-guide.png')
(p/'walk-guides.json').write_text(json.dumps({'source_frames':[0,10,20,30,40,50,60,70],'views':views,'all_guides_only':True,'common_display_matrix':[.8,0,0,.8,-13,80],'source_segmented_render_not_final_art':True},indent=2))
