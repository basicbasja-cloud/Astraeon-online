"""Fixed whole-guide transform, not output art or recovered painted joint labels."""
from pathlib import Path
from PIL import Image
import json
P=Path(__file__).resolve().parent
D=json.loads((P.parent/'ro-core-motion-v53/source/guide-display-affine.json').read_text());print(D)
for view in ['S','SW','NW','N','NE','E','SE']:
 board=Image.new('RGBA',(1536,1024));names=['complete_head','body_with_cape','left_arm','right_arm','left_leg','right_leg','cape','body_no_cape']
 for i,n in enumerate(names):
  im=Image.open(P/'source'/f'{view}-{i:02}-{n}.png').convert('RGBA');s=D['scale'];a=Image.new('RGBA',(384,512));# Same source camera placement for every component.
  im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS);a.alpha_composite(im,(round(D['translation'][0]),round(D['translation'][1])));board.alpha_composite(a,(i%4*384,i//4*512))
 board.save(P/'inputs'/f'{view}-isolated-part-guide.png');bg=Image.new('RGBA',board.size,(40,43,48,255));bg.alpha_composite(board);bg.convert('RGB').save(P/'inputs'/f'{view}-isolated-part-guide-preview.png')
