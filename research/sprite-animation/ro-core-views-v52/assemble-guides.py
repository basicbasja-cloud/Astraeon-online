from pathlib import Path
from PIL import Image
import json,shutil
P=Path(__file__).resolve().parent;m=json.loads((P.parent/'pickup-sixteen-v48/source/display-bind.json').read_text())['matrix'];s,tx,ty=m[0],m[4],m[5];sheet=Image.new('RGBA',(1536,1024))
for i,view in enumerate(['S','SW','W','NW','N','NE','E','SE']):
 im=Image.open(P/'source'/f'neutral-{view}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC);sheet.alpha_composite(im,(i%4*384,i//4*512))
sheet.save(P/'inputs/neutral-eight-camera-guide.png')
shutil.copyfile(P.parent/'recovery-key-v39/renders/review/full/00.png',P/'inputs/approved-front-family.png');shutil.copyfile(P.parent/'ro-motion-lab-v51/inputs/neutral-N.png',P/'inputs/rear-family.png')
