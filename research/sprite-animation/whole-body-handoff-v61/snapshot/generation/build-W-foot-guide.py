from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json
p=Path('work/all-actions-v61/generation');orig=Image.open(p/'W-candidate1/native-keys/00.png').convert('RGBA');bank=Image.new('RGBA',(1536,1024));d=ImageDraw.Draw(bank)
for i in range(8):
 im=Image.open(p/f'W-candidate1/native-keys/{i:02}.png').convert('RGBA');a=np.array(im);a[430:480,143:245]=0;im=Image.fromarray(a);im.alpha_composite(orig.crop((143,430,245,480)),(143,430));x=i%4*384;y=i//4*512;bank.alpha_composite(im,(x,y));d.rectangle((x+2,y+2,x+381,y+509),outline=(0,170,255,255),width=2);d.text((x+12,y+10),f'GUIDE ONLY {i}',fill=(0,170,255,255))
bank.save(p/'W-foot-lock-guide.png');(p/'W-foot-lock-guide.json').write_text(json.dumps({'guide_only':True,'never_final_art':True,'neutral_boot_guide_region':[143,430,245,480],'whole_pose_redraw_required':True},indent=2))
# Adapt fixed-grid native importer to E with source-neutral-only calibration.
s=(p/'build-W-candidate1.py').read_text().replace("out=g/'W-candidate1'","out=g/'E-candidate1'").replace('exec-b5d48513-6015-4965-b938-9198c4cb72d9.png','exec-5dfe248b-db07-496b-ae59-4857d8ba2a52.png').replace('frames/idle/W/00.png','frames/idle/E/00.png').replace('W-split-drape5-motion-case.json','E-split-drape4-motion-case.json').replace('whole-body W candidate','whole-body E candidate');assert Path('research/sprite-animation/pickup-views-v55/E-split-drape4-motion-case.json').exists()
(p/'build-E-candidate1.py').write_text(s)
