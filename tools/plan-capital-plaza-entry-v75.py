"""Resolve the retained infill home's actual door orientation, using visible bounds."""
import json,math,hashlib
from pathlib import Path
from shapely.geometry import MultiPoint,LineString,Polygon,box
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v75';raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw);p=json.loads((O/'plan.json').read_text());assert not p.get('plazaEntryCorrection')
name='ro3-infill-approach-1';lots={l['id']:l for l in p['lots']};objects={o['id']:o for o in s['objects']};l=lots[name];before=l['center'][:];turn=-math.pi/2
polys={n:MultiPoint([v[:2] for a in objects[n]['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull for n in lots}
roads=unary_union([LineString(r['centerline']).buffer(r['width']/2+.35,cap_style=2,join_style=2) for r in p['roads']]);square=box(108,132,148,156).buffer(4,quad_segs=12);courts=unary_union([Polygon(c['polygon']) for c in p['courtyards']]);obstacles=unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.2) for o in s['objects'] if o['id'] not in lots for a in o['parts'] if a['role']=='solid'])
q=rotate(polys[name],-90,origin=before);offsets=sorted([(i*.1,j*.1) for i in range(-20,21) for j in range(-20,21)],key=lambda q:q[0]**2+q[1]**2)
for dx,dy in offsets:
 body=translate(q,dx,dy)
 if body.intersects(roads) or body.intersects(obstacles) or body.intersection(square).area>.001 or body.intersection(courts).area>.001:continue
 if any(body.distance(poly)<.75-1e-5 for n,poly in polys.items() if n!=name):continue
 break
else:raise AssertionError('No clear actual entrance orientation')
l['center']=[round(before[0]+dx,5),round(before[1]+dy,5)];l['angle']+=turn;l['frontageOffset']=math.pi/2;l['lot']=list(translate(rotate(Polygon(l['lot']),-90,origin=before),dx,dy).exterior.coords)[:-1]
p['plazaEntryCorrection']={'id':name,'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'before':before,'after':l['center'],'rotation':turn,'actualDoorDirection':[0,1],'frontageOffset':math.pi/2,'completeModelPreserved':True}
(O/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print(json.dumps(p['plazaEntryCorrection']))
