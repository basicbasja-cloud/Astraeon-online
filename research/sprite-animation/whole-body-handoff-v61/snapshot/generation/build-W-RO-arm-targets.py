from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation
import numpy as np,json
p=Path('work/all-actions-v61/generation');raw=Image.open('/workspace/generated_images/exec-e5e09cf6-6c9c-4885-ac90-9913f9b324bc.png').convert('RGBA');out=Image.new('RGBA',(1536,1024));targets={1:(163,343),3:(153,338),4:(170,343),5:(203,348),6:(220,348),7:(205,348)}
for i in range(8):
 x=i%4*384;y=i//4*512;a=np.array(raw.crop((x,y,x+384,y+512)));allowed=np.zeros((512,384),bool);allowed[130:500,80:335]=True;lab,n=label((a[:,:,3]>=128)&allowed);areas=np.bincount(lab.ravel());areas[0]=0;owner=int(np.argmax(areas));others=[int(v)for k,v in enumerate(areas)if k and k!=owner and v>=40];assert not others,(i,others);keep=binary_dilation(lab==owner,iterations=3)&allowed;a[~keep]=0;out.alpha_composite(Image.fromarray(a),(x,y))
d=ImageDraw.Draw(out)
for i in range(8):
 x=i%4*384;y=i//4*512;d.rectangle((x+2,y+2,x+381,y+509),outline=(0,170,255,255),width=2);d.text((x+12,y+12),f'{i} '+('ARM TARGET' if i in targets else 'KEEP EXACT'),fill=(0,170,255,255))
 if i in targets:
  cx,cy=targets[i];d.ellipse((x+cx-9,y+cy-9,x+cx+9,y+cy+9),outline=(255,30,60,255),width=3);d.line((x+cx-4,y+cy,x+cx+4,y+cy),fill=(255,30,60,255),width=1)
out.save(p/'W-walk-RO-arm-targets.png');(p/'W-walk-RO-arm-targets.json').write_text(json.dumps({'guide_only':True,'near_hand_centers':targets,'unchanged_keys':[0,2]},indent=2))
