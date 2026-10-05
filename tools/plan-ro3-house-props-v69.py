"""Read-only plan for small house goods, protecting streets and service access."""
import json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'))
w=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())
roads=[h['hull'](s['vertices']) for s in w['terrain']['surfaces'] if s.get('centerline') and s.get('width',0)>=1.8]
services=[s['position'][:2] for o in w['objects'] for s in o.get('services',[])]
patrols=[pair for o in w['objects'] for a in o.get('walkers',[]) for pair in zip(a['route'],a['route'][1:]+a['route'][:1])]
solids=[h['hull'](p['vertices']) for o in w['objects'] for p in o['parts'] if p['role']=='solid']
accepted=[]
for o in w['objects']:
 core=next((p for p in o['parts'] if p['id'].endswith('-ground-core') or p['id'].startswith('side-v59-') and p['id'].endswith('-lower-walls')),None)
 if not core:continue
 outline=h['hull'](core['vertices'])
 for a,b in sorted(zip(outline,outline[1:]+outline[:1]),key=lambda e:-(e[1][0]-e[0][0])):
  import math
  length=math.dist(a,b);t=((b[0]-a[0])/length,(b[1]-a[1])/length);normal=(t[1],-t[0])
  for s in (.70,length-.70):
   c=(a[0]+t[0]*s+normal[0]*.58,a[1]+t[1]*s+normal[1]*.58)
   poly=h['rectangle'](c,t,normal,.82,.68)
   if not all(h['inside'](p,w['terrain']['walkablePolygon']) for p in poly):continue
   if any(h['overlap'](poly,p,.10) for p in roads+solids+[r['polygon'] for r in accepted]):continue
   if any(h['segment_overlap'](poly,a,b,.55) for a,b in patrols):continue
   if any(h['inside'](p,poly) or min(h['distance'](p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))<1 for p in services):continue
   accepted.append({'owner':o['id'],'center':c,'tangent':t,'normal':normal,'polygon':poly,'kind':('barrel' if len(accepted)%3==0 else 'crate' if o['family'] in ('market','workshop') else 'planter')})
   break
  else:continue
  break
path=ROOT/'authoring/ro3-house-props-v69.json'
path.write_text(json.dumps({'sourcePass':69,'protected':['road polygons >=1.8','patrol capsules .55','service approach 1.0','all existing solids .10','other props .10'],'props':accepted},indent=2)+'\n')
print('Planned',len(accepted),'grounded house accessory stations')
