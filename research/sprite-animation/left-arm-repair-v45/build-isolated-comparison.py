from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).resolve().parent;views=['S','SE','E','NE','N','NW','W','SW'];rois=json.loads((P/'comparison-layout.json').read_text())['crop_boxes'];plate=Image.new('RGBA',(960,2048),(36,40,47,255));d=ImageDraw.Draw(plate)
for row,v in enumerate(views):
 x0,y0,x1,y1=rois[v];scale=min(220/(x1-x0),230/(y1-y0));size=(round((x1-x0)*scale),round((y1-y0)*scale))
 for col,(bank,i,label) in enumerate([('before-arm-visibility',0,'BEFORE REST'),('arm-visibility',0,'AFTER REST'),('before-arm-visibility',3,'BEFORE BEND'),('arm-visibility',3,'AFTER BEND')]):
  im=Image.open(P/f'{bank}/isolated/{v}/{i:02}.png').crop(rois[v]).resize(size,Image.Resampling.LANCZOS);plate.alpha_composite(im,(col*240+(240-size[0])//2,row*256+22));d.text((col*240+6,row*256+4),v+' '+label,fill='white')
plate.save(P/'isolated-left-before-after.png');print('Actual isolated source surface comparison built; same crop boxes as normal review')
