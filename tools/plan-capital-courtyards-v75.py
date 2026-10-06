"""Turn selected complete frontage models inward around purposeful owned courts."""
import json,hashlib,math
from pathlib import Path
from shapely.geometry import MultiPoint,Polygon,LineString,box
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v75';raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw);p=json.loads((O/'plan.json').read_text());assert not p.get('courtyardRefinement')
objects={o['id']:o for o in s['objects']};lots={l['id']:l for l in p['lots']}
polys={n:MultiPoint([v[:2] for a in objects[n]['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull for n in lots}
roads=unary_union([LineString(r['centerline']).buffer(r['width']/2+.35,cap_style=2,join_style=2) for r in p['roads']]);moves=[]
courts=[{'id':'artisan-court','name':'Artisans’ Court','center':[103,163],'polygon':[[98.8,159.5],[111,159.5],[111,169.1],[98.8,169.1]],'feature':'Shared well, outdoor craft tables, benches and local noticeboard','homes':['capital-townhouse-092','frontage-copper-shop','capital-townhouse-080','capital-residential-052-b','capital-residential-058-a']},
 {'id':'willow-court','name':'Willow Court','center':[152,200],'polygon':[[146.3,198.2],[162.5,198.2],[162.5,202.2],[146.3,202.2]],'feature':'Neighborhood well, planted seats and gathering space','homes':['district-southwest-lodge','capital-market-031-a','frontage-cobbler','capital-market-062-a']}]
offsets=sorted([(i*.1,j*.1) for i in range(-15,16) for j in range(-15,16)],key=lambda q:q[0]**2+q[1]**2)
for court in courts:
 for n in court['homes']:
  l=lots[n];before=l['center'][:];q=rotate(polys[n],180,origin=before)
  for dx,dy in offsets:
   candidate=translate(q,dx,dy)
   if candidate.intersects(roads):continue
   if any(candidate.distance(other)<.75-1e-5 for name,other in polys.items() if name!=n):continue
   break
  else:raise AssertionError(('No clear inward placement',n))
  l['center']=[round(before[0]+dx,5),round(before[1]+dy,5)];l['angle']+=math.pi;l['lot']=list(translate(rotate(Polygon(l['lot']),180,origin=before),dx,dy).exterior.coords)[:-1];l['courtyard']=court['id'];polys[n]=candidate
  moves.append({'id':n,'before':before,'after':l['center'],'rotation':math.pi,'court':court['id']})
 # Entry passages remain between models; the court is an owned pedestrian space.
 assert not Polygon(court['polygon']).intersects(roads)
 assert all(Polygon(court['polygon']).intersection(q).area<.001 for q in polys.values()),court['name']
p['courtyards']=courts;p['courtyardRefinement']={'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'moves':moves,'completeModelsPreserved':True,'publicStreetWidthsUnchanged':True}
(O/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print('INWARD COURTS',len(courts),'whole models',len(moves));print(json.dumps(moves))
