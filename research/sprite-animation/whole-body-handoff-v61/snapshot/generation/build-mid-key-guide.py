from pathlib import Path
from PIL import Image,ImageDraw
import json
p=Path('work/all-actions-v61/generation');raw=Image.open(p/'S-down-layout2/raw.png').convert('RGBA');left=raw.crop((1152,0,1536,512));right=raw.crop((0,512,384,1024));mid=Image.new('RGBA',(384,512));mid.alpha_composite(left)
# Source-only guide: fixed piecewise Y map202->220 and440->440.
# It is NEVER a final animation frame. Feet in GUIDE retain original registration.
body=left.crop((0,202,384,440)).resize((384,220),Image.Resampling.BICUBIC);mid.paste(body,(0,220));mid.paste((0,0,0,0),(0,0,384,220))
# The duplicated original left frame includes guides; rebuild only frame guides.
for im,num in [(left,'A / existing03'),(mid,'B / NEW BETWEEN'),(right,'C / existing04')]:
 d=ImageDraw.Draw(im);d.rectangle((2,2,381,509),outline=(0,170,255,255),width=2);d.rectangle((7,7,220,30),fill=(0,0,0,0));d.text((12,10),num,fill=(0,170,255,255));d.line((12,476,100,476),fill=(0,170,255,255),width=2);d.line((284,476,371,476),fill=(0,170,255,255),width=2)
d=ImageDraw.Draw(mid);d.line((105,220,125,220),fill=(255,65,70,255),width=2)
board=Image.new('RGBA',(1152,512));board.alpha_composite(left,(0,0));board.alpha_composite(mid,(384,0));board.alpha_composite(right,(768,0));board.save(p/'S-mid-key-guide.png')
(p/'S-mid-key-guide.json').write_text(json.dumps({'role':'Internal pose guide only, NEVER final art','source_keys':[3,4],'middle_y_guide_map':[[202,220],[440,440]],'foot_guide_reused_only':True,'final_frame_pixel_policy':'Native redraw normalized only by known shared panel geometry; no fitted joints/bbox/sole'},indent=2)+'\n')
