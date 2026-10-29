"""Compare two SAM head-mask centroids to retained source-head displacement.

SAM masks are unapproved semantic proposals and centroid motion is diagnostic.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research'
A=P/'swordsman-pickup-sw08-sam-20261029/head/masks'
B=P/'swordsman-pickup-sw16-head-sam-20261029'
GUIDE=ROOT/'docs/character-factory/review/patch001-swordsman-pickup-35frame-20261029/manifest.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def centroid(path):
 a=np.array(Image.open(path).convert('L'))>127;y,x=np.where(a)
 if len(x)==0:raise ValueError('Empty SAM mask')
 return {'centroid_tile_px':[float(x.mean()*384/1254),float(y.mean()*384/1254+17)],'mask_source_pixels':int(len(x)),'source_bbox':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'sha256':sha(path)}
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 g=json.loads(GUIDE.read_text())['views']['SW']['frames'];delta=np.array(g[16]['landmarks']['head'])-np.array(g[8]['landmarks']['head']);rows=[]
 for idx in (0,2):
  first=centroid(A/f'{idx}.png')
  for label in ('original','bounded'):
   later=centroid(B/label/'masks'/f'{idx}.png');movement=np.array(later['centroid_tile_px'])-np.array(first['centroid_tile_px']);residual=movement-delta
   rows.append({'mask_candidate':idx,'frame16_variant':label,'frame08':first,'frame16':later,'paint_centroid_delta_tile_px':movement.tolist(),'source_head_delta_tile_px':delta.tolist(),'difference_runtime_px':float(np.linalg.norm(residual)*240/768)})
 out.mkdir(parents=True);report={'status':'SAM_MASK_CENTROID_DIAGNOSTIC_NOT_ANATOMICAL_APPROVAL','frames':[8,16],'guide_sha256':sha(GUIDE),'common_canvas_scale':'384px crop from 768px guide; runtime factor 240/768','results':rows,'limitations':['SAM candidates have different omissions and may include scarf or omit ear; area and centroid are not anatomy.','Only two non-adjacent key poses; foot, body, in-betweens and game remain unverified.'],'runtime_admitted':False};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
