"""Original 2-bone gait pose diagram; no source artwork is modified."""
from pathlib import Path
import math
from PIL import Image,ImageDraw
out=Path(__file__).resolve().parents[1]/'authoring/characters/gait-v49';out.mkdir(exist_ok=True)
im=Image.new('RGBA',(2048,1024));g=ImageDraw.Draw(im)
for frame in range(8):
 col,row=frame%4,frame//4;phase=frame/8;lift=.025*math.cos(phase*math.tau*2)
 def p(v):
  x,y,z=v;return(col*512+256+x*180,row*512+430+y*92-z*193)
 hipz=.98+lift
 # Shared torso, opposite arm travel and fixed front view.
 hip=(0,0,hipz);shoulder=(0,0,1.64+lift);head=(0,0,1.95+lift)
 g.line([p(hip),p(shoulder)],fill='#738ca6',width=14);hx,hy=p(head);g.ellipse((hx-34,hy-36,hx+34,hy+36),fill='#738ca6')
 for side in (-1,1):
  q=(phase+(0 if side==-1 else .5))%1
  stance=q<.5;y=.46-1.84*q if stance else -.46+1.84*(q-.5);z=0 if stance else .32*math.sin((q-.5)*math.tau)
  hx=side*.23;dy=y;dz=z-hipz;dist=min(1.139,math.hypot(dy,dz));length=.57
  along=dist/2;across=math.sqrt(max(0,length**2-along**2));uy,uz=dy/dist,dz/dist
  knee=(hx,uy*along-uz*across,hipz+uz*along+uy*across);foot=(hx,y,z);color='#e76f65' if side==-1 else '#529ced'
  g.line([p((hx,0,hipz)),p(knee),p(foot)],fill=color,width=18)
  for point,r in [(knee,13),(foot,16)]:
   x0,y0=p(point);g.ellipse((x0-r,y0-r,x0+r,y0+r),fill=color)
  # Opposite arms swing with the legs; arm lengths remain constant.
  a=(side*.29,0,1.58+lift);b=(side*.38,-y*.45,1.21+lift);c=(side*.43,-y*.65,1.0+lift)
  g.line([p(a),p(b),p(c)],fill=color,width=14)
im.save(out/'south-eight-poses-guide.png')
print(out/'south-eight-poses-guide.png')
