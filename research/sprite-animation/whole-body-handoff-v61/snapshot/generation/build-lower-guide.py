from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
p=Path('work/all-actions-v61/generation');sheet=Image.new('RGBA',(1536,512));d=ImageDraw.Draw(sheet);notes=[]
for j,i in enumerate(range(4,8)):
 new=Image.open(p/'S-candidate6/native-keys'/f'{i:02}.png').convert('RGBA');old=Image.open(p/'S-candidate5/native-keys'/f'{i:02}.png').convert('RGBA')
 # GUIDE ONLY: restore leg geometry before requesting a complete native redraw.
 # This composite is NEVER included in final art or evaluated as animation.
 a=np.array(new);a[380:481,140:292]=0;new=Image.fromarray(a)
 patch=old.crop((140,380,275,481));new.alpha_composite(patch,(140,380));sheet.alpha_composite(new,(384*j,0))
 x=j*384;d.rectangle((x+2,2,x+381,509),outline=(0,170,255,255),width=2);d.text((x+12,10),f'POSE GUIDE ONLY {i}',fill=(0,170,255,255));d.line((x+135,476,x+270,476),fill=(0,170,255,255),width=1)
 notes.append({'key':i,'source_body':'candidate6','source_legs':'candidate5','guide_only_lower_region':[140,380,292,481],'never_final_art':True})
sheet.save(p/'S-leg-lock-guide.png');(p/'S-leg-lock-guide.json').write_text(json.dumps(notes,indent=2))
