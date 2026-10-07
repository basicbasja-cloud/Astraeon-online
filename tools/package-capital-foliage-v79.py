"""Preserve the original generated RGBA pixels as a new lossless candidate."""
import json,hashlib,shutil
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];source=Path('/workspace/generated_images/exec-f63058c8-d601-4461-b1d5-1ce101b01299.png');master=R/'authoring/materials/wayfarer-conifer-v79-source.png';asset=R/'assets/wayfarer-conifer-v79.webp'
assert source.exists() and not master.exists() and not asset.exists(),'One-shot new destination only'
request=json.loads(Path('/tmp/astraeon-foliage-v79-request.json').read_text());shutil.copyfile(source,master)
im=Image.open(master);assert im.mode=='RGBA' and im.size==(1254,1254)
im.save(asset,lossless=True,exact=True,method=6)
a=np.asarray(im);decoded=np.asarray(Image.open(asset).convert('RGBA'));assert np.array_equal(a,decoded),'Lossless RGBA byte comparison'
alpha=a[:,:,3];assert alpha.min()==0 and alpha.max()==255 and .5<(alpha>=31).mean()<.7
rgb=a[:,:,:3].astype(float)/255;linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
spec={'file':asset.relative_to(R).as_posix(),'grid':[1,1],'tile':0,'worldSize':2.4,'paletteDetail':.78,'meanLinearRGB':np.average(linear.reshape(-1,3),axis=0,weights=alpha.reshape(-1)+1e-6).round(7).tolist(),'anisotropy':4,'alphaCutoff':.12}
report={'revision':79,'origin':'Host-native ImageGen edit of original Astraeon project foliage; no reference-game pixels imported','provider':'ImageGen','generatedPath':str(source),'request':request,'master':master.relative_to(R).as_posix(),'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'assetSHA256':hashlib.sha256(asset.read_bytes()).hexdigest(),'size':list(im.size),'assetBytes':asset.stat().st_size,'texture':spec,'originalSourcePreserved':True,'losslessRGBAExact':True,'alphaCoverageAtCutoff':float((alpha>=31).mean()),'validation':'Original output inspected; dimensions/alpha/lossless pixels verified; native/runtime adoption and visual acceptance pending'}
(R/'authoring/materials/wayfarer-conifer-v79.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('request','texture')},indent=2))
