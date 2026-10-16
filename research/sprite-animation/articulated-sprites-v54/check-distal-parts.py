"""Check authored distal boot parts for detached solid pixels outside the main boot.
A bounded alpha-component check, not an automatic foot or anatomical-owner detector.
"""
from pathlib import Path
from PIL import Image
from scipy.ndimage import label,find_objects
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;out={}
def inspect(path,start):
 a=np.array(Image.open(path))[:,:,3]>=128;a[:int(np.ceil(start))]=False;lab,n=label(a);parts=[]
 for i,s in enumerate(find_objects(lab),1):
  if s:parts.append({'area':int((lab[s]==i).sum()),'bbox':[s[1].start,s[0].start,s[1].stop,s[0].stop]})
 assert parts,'No solid distal pixels';main=max(parts,key=lambda r:r['area']);x0,y0,x1,y1=main['bbox'];bad=[r for r in parts if r is not main and (r['bbox'][0]<x0-2 or r['bbox'][1]<y0-2 or r['bbox'][2]>x1+2 or r['bbox'][3]>y1+2)];return {'pass':not bad,'components':parts,'detached_outside_2px_margin':bad,'texture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_distal_y':start}
for v in ['S','SW','W','NW','N','NE','E','SE']:
 d=json.loads((P/(('' if v=='W' else v+'-')+'walk-rig-contract.json')).read_text());out[v]={}
 for side in ['left','right']:
  n=side+'_leg';r=d['definitions'][n];out[v][side]=inspect(P/r['texture'],r['bands'][3])
negative=inspect(P/'SE-negative-neighbor-boot/right_leg.png',458);assert not negative['pass'];passed=all(r['pass'] for v in out.values() for r in v.values());(P/'distal-parts-qa.json').write_text(json.dumps({'pass':passed,'views':out,'actual_SE_neighbor_boot_negative':negative,'scope':'Authored flat-foot distal regions only. Separated components outside the main solid boot require review; this does not infer body ownership or validate hidden joints.'},indent=2)+'\n');print({v:{s:r['pass'] for s,r in d.items()} for v,d in out.items()});assert passed
