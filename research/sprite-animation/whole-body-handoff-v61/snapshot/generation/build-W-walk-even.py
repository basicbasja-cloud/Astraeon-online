from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation
import numpy as np,json,hashlib
p=Path('work/all-actions-v61/generation');out=p/'W-walk-candidate1';(out/'native-even').mkdir(parents=True,exist_ok=True)
raws={k:Image.open('/workspace/generated_images/'+f).convert('RGBA')for k,f in [('base','exec-e5e09cf6-6c9c-4885-ac90-9913f9b324bc.png'),('arm','exec-7e03ffbb-7a07-46af-9ef1-ffb507ea9a33.png')]};keys=[];notes=[]
for i in range(8):
 kind='base'if i in [0,2]else'arm';raw=raws[kind];x=i%4*384;y=i//4*512;a=np.array(raw.crop((x,y,x+384,y+512)));allowed=np.zeros((512,384),bool);allowed[130:500,80:335]=1;lab,n=label((a[:,:,3]>=128)&allowed);areas=np.bincount(lab.ravel());areas[0]=0;owner=int(np.argmax(areas));assert not any(v>=40 for k,v in enumerate(areas)if k and k!=owner);keep=binary_dilation(lab==owner,iterations=3)&allowed;a[~keep]=0;im=Image.fromarray(a);im.save(out/'native-even'/f'{i:02}.png');keys.append(im);notes.append({'key':i,'source':kind,'matte_rect':[80,130,335,500],'sha256':hashlib.sha256((out/'native-even'/f'{i:02}.png').read_bytes()).hexdigest()})
for name,order in [('left',list(range(8))),('right',[1,2,3,4,5,6,7,0])]:
 sheet=Image.new('RGBA',(1536,1024))
 for i,j in enumerate(order):sheet.alpha_composite(keys[j],(i%4*384,i//4*512))
 d=ImageDraw.Draw(sheet)
 for i,j in enumerate(order):
  x=i%4*384;y=i//4*512;d.rectangle((x+2,y+2,x+381,y+509),outline=(0,170,255,255),width=2);d.text((x+12,y+12),f'{name} {i}:key{j}',fill=(0,170,255,255))
 sheet.save(p/f'W-walk-mid-{name}.png')
(out/'even-import.json').write_text(json.dumps({'keys':notes,'per_key_registration':False,'complete_native_body':True,'art_approval':False},indent=2))
