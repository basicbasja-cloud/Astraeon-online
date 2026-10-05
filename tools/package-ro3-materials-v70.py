"""Package original generated game artwork unchanged as lossless textures."""
import json,hashlib,shutil
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for name,source,size,detail,cutoff in [('street-stone','/workspace/generated_images/exec-f34489ce-1360-456f-a796-45391adb1e2e.png',8,.76,None),('conifer','/workspace/generated_images/exec-fbaf32d5-b5b2-4644-b32f-f82dfb22b05d.png',2.4,.82,.12)]:
 master=ROOT/f'authoring/materials/wayfarer-{name}-v70-source.png';asset=ROOT/f'assets/wayfarer-{name}-v70.webp'
 if Path(source).exists():shutil.copy(source,master)
 assert master.exists(),f'Original artwork required: {master}'
 im=Image.open(master).convert('RGBA' if cutoff else 'RGB');im.save(asset,lossless=True,method=6)
 a=np.asarray(im,dtype=float)/255;rgb=a[:,:,:3];linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);weights=a[:,:,3] if cutoff else np.ones(a.shape[:2]);spec={'file':asset.relative_to(ROOT).as_posix(),'grid':[1,1],'tile':0,'worldSize':size,'paletteDetail':detail,'meanLinearRGB':np.average(linear.reshape(-1,3),axis=0,weights=weights.reshape(-1)+1e-6).round(7).tolist(),'anisotropy':4}
 if cutoff:spec['alphaCutoff']=cutoff
 report={'sourcePass':70,'origin':'Original generated painterly game material; no reference pixels imported','master':master.relative_to(ROOT).as_posix(),'size':list(im.size),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'texture':spec,'structure':'Broad irregular rounded street stones; no fine hexagon repeat' if not cutoff else 'Evergreen needle boughs with transparent organic tips'};(ROOT/f'authoring/materials/wayfarer-{name}-v70.json').write_text(json.dumps(report,indent=2)+'\n');print(name,im.size,spec['file'])
