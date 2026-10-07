"""Rebalance the saved capital's building stock, preserving its public streets.

Pair consolidation uses actual roof envelopes and excludes plaza/court fronts.
Shared block paving remains authoritative; this is not another city annex.
"""
import json, math, hashlib, collections
from pathlib import Path
from shapely.geometry import MultiPoint, Polygon, LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76';O.mkdir(exist_ok=True)
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
p=json.loads((R/'docs/review/wayfarer-capital-v75/native-plan.json').read_text())
assert not p.get('architectureRevision'), 'Architecture plan has already been applied'
objects={o['id']:o for o in s['objects']};lots={l['id']:l for l in p['lots']}
protected=set(p['plazaFrontageRefinement']['frontages'])|{n for c in p['courtyards'] for n in c['homes']}
outlines={n:MultiPoint([v[:2] for a in objects[n]['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull for n in lots}
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.35,cap_style=2,join_style=2) for a in p['roads']])
solids=[(o['id'],MultiPoint([v[:2] for v in a['vertices']]).convex_hull) for o in s['objects'] for a in o['parts'] if a['role']=='solid']
proposals=[]
for i,a in enumerate(p['lots']):
 if a['existing'] or a['id'] in protected:continue
 for b in p['lots'][i+1:]:
  if b['existing'] or b['id'] in protected or a['district']!=b['district']:continue
  if abs(math.sin(a['angle']-b['angle']))>.001 or math.cos(a['angle']-b['angle'])<.999:continue
  dx,dy=b['center'][0]-a['center'][0],b['center'][1]-a['center'][1]
  along=dx*math.cos(a['angle'])+dy*math.sin(a['angle']);normal=-dx*math.sin(a['angle'])+dy*math.cos(a['angle'])
  if abs(normal)>.3 or not .5<abs(along)-(a['width']+b['width'])/2<3.2:continue
  left=min(-a['width']/2,along-b['width']/2);right=max(a['width']/2,along+b['width']/2);w=right-left
  if not 8<w<12.3:continue
  x,y=a['center'];off=(left+right)/2;cx=x+off*math.cos(a['angle']);cy=y+off*math.sin(a['angle']);dep=min(a['depth'],b['depth'])-.12
  vs=[(cx+u*math.cos(a['angle'])-v*math.sin(a['angle']),cy+u*math.sin(a['angle'])+v*math.cos(a['angle'])) for u,v in [(-w/2-.30,-dep/2-.30),(w/2+.30,-dep/2-.30),(w/2+.30,dep/2+1.15),(-w/2-.30,dep/2+1.15)]]
  q=Polygon(vs)
  if q.intersects(roads):continue
  if any(q.distance(poly)<.75-1e-5 for n,poly in outlines.items() if n not in (a['id'],b['id'])):continue
  if any(q.intersection(poly).area>.005 for n,poly in solids if n not in (a['id'],b['id'])):continue
  proposals.append((abs(along),a['id'],b['id'],[round(cx,5),round(cy,5)],round(w-.10,5),round(dep,5)))
used=set();merges=[]
# Balance larger buildings between wards; never merge all frontage pairs.
district_counts=collections.Counter()
for _,a,b,center,w,dep in sorted(proposals):
 if a in used or b in used or district_counts[lots[a]['district']]>=4:continue
 if len(merges)>=16:break
 used.update((a,b));district_counts[lots[a]['district']]+=1
 keep=lots[a];keep.update(center=center,width=w,depth=dep,mergedFrom=[a,b],architectureType='merchant-hall' if keep['family']=='market' else 'gallery-villa' if len(merges)%3==1 else 'twin-gable')
 keep['lot']=list(unary_union([Polygon(keep['lot']),Polygon(lots[b]['lot'])]).convex_hull.exterior.coords)[:-1]
 merges.append({'kept':a,'removed':b,'center':center,'width':w,'district':keep['district'],'type':keep['architectureType']})
removed={m['removed'] for m in merges};p['lots']=[l for l in p['lots'] if l['id'] not in removed]
assert len(merges)>=8,('Too few safe paired plots',len(merges))
families=['front-gable','half-hip','cross-gable','guild-mansard','oriel-house','craft-lodge']
assignments={}
for l in sorted((l for l in p['lots'] if not l['existing']),key=lambda l:(l['district'],l['center'][1],l['center'][0])):
 if l.get('mergedFrom'):assignments[l['id']]=l['architectureType'];continue
 neighbors=sorted((math.dist(l['center'],o['center']),o['id']) for o in p['lots'] if o['id'] in assignments)
 forbidden={assignments[n] for distance,n in neighbors[:2] if distance<18}
 preferred=['oriel-house','cross-gable','guild-mansard','half-hip','front-gable','craft-lodge'] if l.get('plazaFacing') else ['craft-lodge','cross-gable','front-gable','oriel-house','half-hip','guild-mansard'] if l['family']=='workshop' else families
 start=int(hashlib.sha256(l['id'].encode()).hexdigest()[:4],16)%len(preferred)
 choices=preferred[start:]+preferred[:start]
 l['architectureType']=next(t for t in choices if t not in forbidden);assignments[l['id']]=l['architectureType']
 l['clay']=['roofClayWarm','roofClayOchre','roofClayRose'][int(hashlib.sha256((l['district']+l['id']).encode()).hexdigest()[:4],16)%3]
p['newHouses']=sum(not l['existing'] for l in p['lots'])
for key in ('densityRefinement','neighborhoodRefinement','ro3StreetScaleRefinement'):
 if key in p:
  p[key]['moves']=[m for m in p[key].get('moves',[]) if m['id'] not in removed]
  p[key]['added']=[n for n in p[key].get('added',[]) if n not in removed]
p['architectureRevision']={'version':76,'baselineSourceSHA256':hashlib.sha256(raw).hexdigest(),'pairedPlotConsolidations':merges,'families':dict(collections.Counter(assignments.values())),'beforeBuildings':172,'afterBuildings':len(p['lots']),'publicStreetWidthsUnchanged':True,'plazaAndCourtDirectionsRetained':True,'densityGoal':'Varied inhabited blocks with larger institutions and shared plots, not maximum house count'}
for spec in p['landmarks']:
 spec['architectureType']={'capital-council-chambers':'hipped-palazzo','capital-grand-archive':'rose-nave-and-stair-tower','capital-trade-exchange':'long-market-hall-and-belfry'}[spec['id']]
 if spec['id']=='capital-trade-exchange':spec.update(center=[192.5,126],width=19,depth=13.5,front=[192.5,137])
for name in ('plan.json','native-plan.json'):(O/name).write_text(json.dumps(p,indent=2)+'\n')
(O/'architecture-plan.json').write_text(json.dumps(p['architectureRevision'],indent=2)+'\n')
print(json.dumps(p['architectureRevision'],indent=2))
