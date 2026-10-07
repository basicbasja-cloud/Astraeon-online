"""Select original sheltered fronts by owned plot, actual door and closed routes.
RO3 house03:35 supports low secondary roofs and layered property fronts; all
positions and shapes below are original proposals, not recovered RO3 coordinates.
"""
import json,hashlib,math
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint,LineString,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v78/frontage-placement';O.mkdir(parents=True,exist_ok=True)
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert sha=='461fc1142ab22989a3f8d3f3281924eebf7a0b5b714c110e7553c09ad2025275'
s=json.loads(raw);p=json.loads((R/'docs/review/wayfarer-capital-v77/native-plan.json').read_text());owners={o['id']:o for o in s['objects']}
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2,cap_style=2,join_style=2) for a in p['roads']])
feet=unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull for o in s['objects'] for a in o['parts'] if a['role']=='solid'])
patrols=unary_union([LineString(w['route']+[w['route'][0]]).buffer(.38) for o in s['objects'] for w in o.get('walkers',[]) if len(w['route'])>1])
services=unary_union([Point(a['position'][:2]).buffer(1.2) for o in s['objects'] for a in o.get('services',[])]+[Point(a['anchor'][:2]).buffer(1.2) for o in s['objects'] for a in o.get('portals',[])])
allout={l['id']:MultiPoint([v[:2] for a in owners[l['id']]['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull for l in p['lots']}
selected=[];rejected=[]
# Deliberate fronts: prominent west neighborhood, plaza enclosure, then selected
# gabled residences at district approaches. Other roof families remain distinct.
requested={'frontage-riverside','north-garden-house','capital-townhouse-083','capital-townhouse-089','capital-residential-040-b','capital-residential-028-b','capital-residential-044-b','capital-workshop-034-a','capital-workshop-032-b'}
requested|={l['id'] for l in p['lots'] if l.get('architectureType')=='front-gable'}
for l in p['lots']:
 if l['id'] not in requested:continue
 door=next(a for a in owners[l['id']]['parts'] if a['id'].endswith('-door-leaf'))
 dc=[sum(v[i] for v in door['vertices'])/len(door['vertices']) for i in range(2)];angle=l['angle']+l.get('frontageOffset',0)
 def transform(x,y):return (dc[0]+math.cos(angle)*x-math.sin(angle)*y,dc[1]+math.sin(angle)*x+math.cos(angle)*y)
 lot=Polygon(l['lot']);style='entry-gable' if l['family']=='residential' else 'trade-lean-to'
 if l['id'] in ('capital-townhouse-083','north-garden-house','capital-residential-051','capital-residential-041-a'):style='garden-hip'
 if l['id'] in ('frontage-riverside','capital-townhouse-088','capital-residential-077-b','capital-residential-058-b'):style='eave-gallery'
 width=3.10 if l['width']>=5.2 else 2.82;depth=.84
 # Roof attaches at the facade. Pillars leave a full2.2m approach clear.
 roof=Polygon([transform(x,y) for x,y in [(-width/2,-.20),(width/2,-.20),(width/2,depth),(-width/2,depth)]])
 posts=[Polygon([transform(x+dx,depth-.17+dy) for dx,dy in [(-.065,-.065),(.065,-.065),(.065,.065),(-.065,.065)]]) for x in (-width/2+.14,width/2-.14)]
 reason=None
 if not lot.buffer(.03).covers(roof):reason='Roof would leave the owned plot'
 elif roof.intersection(roads).area>.0001:reason='Roof would occupy public street'
 elif any(q.buffer(.08).intersects(feet) or q.buffer(.08).intersects(patrols) or q.buffer(.08).intersects(services) for q in posts):reason='Post would conflict with physical or gameplay use'
 elif any(roof.distance(q)<.75 for n,q in allout.items() if n!=l['id']):reason='Secondary roof would crowd another building'
 if reason:rejected.append({'id':l['id'],'reason':reason});continue
 selected.append({'id':l['id'],'family':l['family'],'district':l['district'],'position':dc+[.04],
   'angle':angle,'width':width,'depth':depth,'style':style,'roofMaterial':l.get('clay','roofClayWarm'),
   'doorTop':max(v[2] for v in door['vertices']),'roofFootprint':list(roof.exterior.coords)[:-1],
   'postFootprints':[list(q.exterior.coords)[:-1] for q in posts],
   'use':'sheltered residence' if l['family']=='residential' else 'covered artisan threshold'})
assert len(selected)>=12,len(selected)
images={m['texture']['file'] for m in s['materials'].values() if m.get('texture')}
report={'baselineCommit':'3cc2c65','beforeSourceSHA256':sha,'frontages':selected,'rejected':rejected,
 'roofTextureWorldSizeBefore':2.4,'roofTextureWorldSizeAfter':3.4,'roofUVFactor':2.4/3.4,
 'materialNames':['roofClayWarm','roofClayRose','roofClayOchre'],'entranceClearWidth':2.2,
 'triangleBudget':10000,'additionalImageAssets':0,'originalImages':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in images},
 'referenceFrames':['04_Houses_Shops_Roofs/Houses_Shops_Roofs_03m35s.jpg','02_Streets_and_Junctions/Streets_and_Junctions_00m50s.jpg'],
 'placementPolicy':'Actual door/owned plot first; open streets, distinct roof families and closed patrol loops preserved',
 'visualAcceptance':'Pending source-matched normal gameplay images'}
(O/'plan.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'selected':len(selected),'ids':[a['id'] for a in selected],'rejected':rejected},indent=2))
