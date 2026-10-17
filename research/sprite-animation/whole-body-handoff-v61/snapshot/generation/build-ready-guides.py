from PIL import Image,ImageDraw
from pathlib import Path
r=Path.cwd();p=r/'work/all-actions-v61/generation'
for v in ['S','W','N','E']:
 bank=Image.new('RGBA',(1536,1024));guide=Image.new('RGBA',bank.size);d=ImageDraw.Draw(bank);dg=ImageDraw.Draw(guide)
 for i in range(8):
  x=i%4*384;y=i//4*512
  for name,sheet in [('idle',bank),('ready',guide)]:
   frame=0 if name=='idle' else i*3;im=Image.open(r/f'research/sprite-animation/core-family-v56/frames/{name}/{v}/{frame:02}.png').convert('RGBA').resize((410,461),Image.Resampling.LANCZOS);sheet.alpha_composite(im,(x-13,y+80))
  for dr in [d,dg]:dr.rectangle((x+2,y+2,x+381,y+509),outline=(0,170,255,255),width=2);dr.text((x+12,y+10),f'{v} READY {i}',fill=(0,170,255,255))
 bank.save(p/f'{v}-ready-layout.png');guide.save(p/f'{v}-ready-poses-guide.png')
