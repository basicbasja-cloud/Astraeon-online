"""Compile pickup checks onto delivered PNGs with one declared bank affine."""
from pathlib import Path
import json,hashlib,shutil,math
P=Path(__file__).resolve().parent;ROOT=P.parents[2];KIT=P;cases=P.parent;D=json.loads((P/'catalog.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cp(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
# Profiles are explicitly rebound to current identity/padded delivery frames.
profiles=KIT/'profiles';profiles.mkdir(exist_ok=True);provenance=[]
for v,case,name in [('N',cases/'ro-motion-lab-v51','pickup'),('W',cases/'pickup-views-v55','W-split-drape5'),('E',cases/'pickup-views-v55','E-split-drape4'),('S',cases/'pickup-views-v55','S-front4')]:
 frames=D['actions']['pickup']['clips'][v]['frames']
 for kind,suffix in [('motion','-motion-case.json'),('contact','-layer-contact-case.json'if v=='S'else'-contact-case.json')]:
  src=case/(name+suffix);q=json.loads(src.read_text());original_sha=sha(src)
  for i,r in enumerate(q['frames']):
   f=frames[i];target={'path':'../'+f['path'],'sha256':f['sha256']}
   if v=='S'and kind=='contact':
    r['composite']=target
    for owner,l in r['layers'].items():
     original=case/l['path'];dest=profiles/'contact-layers/S'/Path(l['path']).name;cp(original,dest);l['path']=str(dest.relative_to(profiles));assert sha(dest)==l['sha256']
   else:r.update(target)
  if v=='N':
   stage=json.loads((cases/'ro-core-views-v52/stage-manifest.json').read_text());bank=next(x for x in stage['items']if x['action']=='pickup'and x['view']=='N')['frames'];affines={(x['scale'],tuple(x['translation']))for x in bank};assert len(affines)==1
   scale,(tx,ty)=affines.pop()
   def rect(r):return [math.floor(r[0]*scale+tx),math.floor(r[1]*scale+ty),math.ceil(r[2]*scale+tx),math.ceil(r[3]*scale+ty)]
   if kind=='motion':q['crown_window']=rect(q['crown_window'])
   else:
    for surface in q['surfaces'].values():surface['window']=rect(surface['window']);surface['budget_px']={axis:math.ceil(value*scale)for axis,value in surface['budget_px'].items()}
   q['common_canvas_transform']={'scale':scale,'translation':[tx,ty],'authority':'ro-core-views-v52/stage-manifest.json','method':'One declared source-bank affine, outward-rounded ROI; no frame fitting. Original declared contact budget scaled and rounded outward; no tightening based on output.'}
  dest=profiles/(v+'-'+kind+'.json');dest.write_text(json.dumps(q,indent=2)+'\n');provenance.append({'profile':str(dest.relative_to(KIT)),'source_case':str(src.relative_to(ROOT)),'source_case_sha256':original_sha,'operation':'Explicit current output path/SHA rebind after visible-RGBA identity/common-canvas proof; clock unchanged; N ROI mapped by declared one-bank affine, original declared contact budget mapped to output pixels.'})
(KIT/'profile-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
