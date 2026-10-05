"""Original cobbles, worn curb stone and bark; editable lossless native textures."""
import json,random,hashlib,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'authoring/materials';r=random.Random(6939);records={}
def save(name,im,size,detail):
 master=out/(name+'-source.png');asset=ROOT/'assets'/(name+'.webp');im.save(master);im.save(asset,lossless=True,method=6)
 a=np.asarray(im,dtype=float)/255;linear=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
 records[name]={'master':master.relative_to(ROOT).as_posix(),'size':list(im.size),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'texture':{'file':asset.relative_to(ROOT).as_posix(),'grid':[1,1],'tile':0,'worldSize':size,'paletteDetail':detail,'meanLinearRGB':linear.mean(axis=(0,1)).round(7).tolist(),'anisotropy':4}}
im=Image.new('RGB',(2048,2048),'#777564');d=ImageDraw.Draw(im)
for row in range(32):
 for col in range(-1,33):
  x=col*64+(row%2)*32;y=row*64;v=r.randrange(-18,19);x0=x+4;y0=y+4;x1=x+61;y1=y+61
  d.rounded_rectangle((x0,y0,x1,y1),radius=r.randrange(11,19),fill=(172+v,165+v,145+v))
  d.arc((x0+1,y0+1,x1-1,y1-1),185,290,fill=(205+v,198+v,174+v),width=3);d.arc((x0+2,y0+2,x1-1,y1-1),5,110,fill=(127+v,123+v,108+v),width=3)
  for _ in range(16):
   px=r.randint(x0+8,x1-8);py=r.randint(y0+8,y1-8);n=r.randrange(-9,10);d.ellipse((px,py,px+3,py+2),fill=(166+v+n,160+v+n,140+v+n))
save('wayfarer-cobbles-v69',im,8,.86)
yy,xx=np.mgrid[:1024,:1024];rng=np.random.default_rng(6939);grain=rng.normal(0,3.2,(1024,1024));noise=grain+6*np.sin(xx/41+yy/78)+4*np.sin(xx/113-yy/94)
im=Image.fromarray(np.stack([185+noise,177+noise,153+noise],axis=2).clip(0,255).astype('uint8'));d=ImageDraw.Draw(im)
for _ in range(1800):
 x,y=r.randrange(1024),r.randrange(1024);v=r.randrange(130,195);d.ellipse((x,y,x+r.randrange(2,7),y+r.randrange(1,4)),fill=(v,v-7,v-23))
for _ in range(48):
 x,y=r.randrange(1024),r.randrange(1024);d.line([(x,y),(x+r.randrange(8,28),y+3),(x+r.randrange(20,48),y+r.randrange(-4,12))],fill=(143,139,120),width=1)
save('wayfarer-curb-stone-v69',im,1.4,.84)
noise=rng.normal(0,2.0,(1024,1024))+8*np.sin(xx/11+np.sin(yy/67)*1.3)+5*np.sin(xx/29+yy/180)
im=Image.fromarray(np.stack([119+noise,86+noise,54+noise],axis=2).clip(0,255).astype('uint8'));d=ImageDraw.Draw(im)
for x in range(-8,1040,18):
 pts=[(x+5*math.sin(y/67+x),y) for y in range(0,1025,16)];d.line(pts,fill=(76,52,32),width=r.randrange(2,5));d.line([(a+3,b) for a,b in pts],fill=(158,117,70),width=2)
for _ in range(35):
 x,y=r.randrange(1024),r.randrange(1024);d.ellipse((x-5,y-17,x+5,y+17),outline=(67,46,29),width=2)
save('wayfarer-tree-bark-v69',im,1.4,.82)
(out/'wayfarer-road-zone-v69.json').write_text(json.dumps({'sourcePass':69,'origin':'Original seeded stone and bark artwork; no reference pixels imported','materials':records},indent=2)+'\n');print('Authored cobbles2048, worn stone1024, bark1024')
