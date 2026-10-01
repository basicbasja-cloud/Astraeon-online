"""Import generated original district artwork into browser-ready sprites.
Pass the original generated atlas path. Fixed reviewed crop rectangles prevent
neighboring silhouettes from leaking into the four independently loaded assets.
"""
from PIL import Image
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
im=Image.open(sys.argv[1] if len(sys.argv)>1 else root/'assets/source/wayfarer-district-atlas-v1.png').convert('RGBA')
rects={'forge':(15,0,630,580),'inn':(640,0,1280,605),'shrine':(35,560,640,1270),'cottage':(660,640,1280,1250)}
# These reviewed rectangles are normalized to the supplied generated atlas size.
for key,rect in rects.items():
 rect=tuple(round(n*im.width/1280) for n in rect);sprite=im.crop(rect)
 px=sprite.load()
 for y in range(sprite.height):
  for x in range(sprite.width):
   r,g,b,a=px[x,y]
   if r>190 and g<80 and b<90 and r>g*2: px[x,y]=(r,g,b,0)
 sprite.save(root/f'assets/wayfarer-{key}-v1.webp',lossless=True)
 print(key,sprite.size)
