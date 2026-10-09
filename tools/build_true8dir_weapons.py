"""Normalize original generated sword views into registered perspective samples."""
from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];B=R/'authoring/characters/builds/swordsman-true8dir-v1';O=R/'assets/characters/swordsman-true8dir-v1';im=Image.open(B/'weapons-generated.png').convert('RGBA');centres=[302,620,908,1236];names=['face','edge','foreshortened','rear'];meta={}
for row,key in enumerate(['weapon-a','weapon-b']):
 atlas=Image.new('RGBA',(64*4,128));views=[]
 for c,name in enumerate(names):
  # Same authored scale for all perspectives: shorter art remains shorter.
  gripY=[405,401,404,407][c] if row==0 else [889,885,887,891][c]
  tipY=[17,17,118,46][c] if row==0 else [520,523,595,548][c]
  x=centres[c];scale=.21;tile=im.transform((64,128),Image.Transform.AFFINE,(1/scale,0,x-32/scale,0,1/scale,gripY-98/scale),resample=Image.Resampling.BICUBIC)
  a=np.array(tile);a[:,:,3][a[:,:,3]>=245]=255;a[a[:,:,3]==0]=0;tile=Image.fromarray(a);atlas.paste(tile,(c*64,0))
  views.append(dict(name=name,rect=[c*64,0,64,128],equipmentAnchor=[32,86],gripContactPoint=[32,98],weaponTip=[32,round(98+(tipY-gripY)*scale,3)]))
 atlas.save(O/(key+'-poses.png'));meta[key]=views
(B/'weapon-samples.json').write_text(json.dumps(meta,indent=2))
