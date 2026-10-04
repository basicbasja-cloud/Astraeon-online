"""Normalize a complete 4x2 study with one canvas transform and shared root.

No per-pose bounding-box alignment, recoloring, boot warping or image cleanup.
The source guide's pelvis registration survives the generated canvas resize.
This creates authoring previews only; it cannot install runtime artwork.
"""
import argparse, json, shutil
from pathlib import Path
from PIL import Image

ap=argparse.ArgumentParser()
ap.add_argument('input',type=Path)
ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--direction',choices=['S','SE','E','NE','N','NW','W','SW'],default='S')
args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
shutil.copy2(args.input,args.output/'painted-source.png')
source=Image.open(args.input).convert('RGBA')
assert abs(source.width/source.height-2)<.005,'Expected a complete four-column, two-row canvas'
canvas=source.resize((1536,768),Image.Resampling.LANCZOS)
canvas.save(args.output/'painted-eight-study.png')
frames=[]
for i in range(8):
    x,y=i%4*384,i//4*384
    frame=canvas.crop((x,y,x+384,y+384))
    frame.save(args.output/f'{args.direction}-{i+1:02d}.png')
    frames.append(frame)
# A shared background makes transparent silhouette/anchor motion readable.
previews=[]
for frame in frames:
    background=Image.new('RGBA',frame.size,(34,45,56,255))
    background.alpha_composite(frame)
    previews.append(background.convert('RGB'))
previews[0].save(args.output/(args.direction.lower()+'-walk-preview.gif'),save_all=True,append_images=previews[1:],duration=110,loop=0)
(args.output/'normalization.json').write_text(json.dumps({
    'candidateOnly':True,'installed':False,'sourceSize':source.size,
    'normalizedCanvas':[1536,768],'frames':8,'layout':[4,2],
    'scale':[1536/source.width,768/source.height],
    'registration':'One whole-canvas transform; no per-frame foot alignment',
    'directions':[args.direction],'otherDirectionsComplete':False
},indent=2)+'\n')
print('Authoring-only eight-pose preview:',args.output)
