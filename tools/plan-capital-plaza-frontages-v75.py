"""Arrange the square's immediate building ring with frontages toward the plaza."""
import json,hashlib,math
from pathlib import Path
from shapely.geometry import MultiPoint,Polygon,LineString,box
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v75';raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw);p=json.loads((O/'plan.json').read_text());assert not p.get('plazaFrontageRefinement')
objects={o['id']:o for o in s['objects']};lots={l['id']:l for l in p['lots']};polys={n:MultiPoint([v[:2] for a in objects[n]['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull for n in lots}
roads=unary_union([LineString(r['centerline']).buffer(r['width']/2+.35,cap_style=2,join_style=2) for r in p['roads']]);square=box(108,132,148,156).buffer(4,quad_segs=12);courts=unary_union([Polygon(c['polygon']) for c in p['courtyards']]);moves=[]
tree_moves=[{'id':f'capital-tree-{i:03}','after':[x,178.2]} for i,x in [(26,119),(32,137)]]
furniture_moves=[{'prefix':f'capital-v75-capital-lamp-{x}-{y}-','delta':[0,dy,0]} for x in (120,136) for y,dy in [(124,3),(176,2.2)]]
furniture_moves=[m for m in furniture_moves if any(a['id'].startswith(m['prefix']) for o in s['objects'] for a in o['parts'])]
obstacles=[]
for owner in s['objects']:
 if owner['id'] in lots:continue
 for part in owner['parts']:
  if part['role']!='solid':continue
  q=MultiPoint([v[:2] for v in part['vertices']]).convex_hull
  relocation=next((m for m in tree_moves if m['id']==owner['id']),None)
  if relocation:q=translate(q,relocation['after'][0]-q.centroid.x,relocation['after'][1]-q.centroid.y)
  furniture=next((m for m in furniture_moves if part['id'].startswith(m['prefix'])),None)
  if furniture:q=translate(q,*furniture['delta'][:2])
  obstacles.append(q.buffer(.2))
protected=unary_union(obstacles)
def move(n,angle,dx,dy,plaza=False):
 l=lots[n];before=l['center'][:];turn=(angle-l['angle']+math.pi)%math.tau-math.pi;q=translate(rotate(polys[n],turn*180/math.pi,origin=before),dx,dy)
 assert not q.intersects(roads),(n,'street')
 assert q.intersection(square).area<.001 and q.intersection(courts).area<.001,(n,'public square or shared court')
 assert not q.intersects(protected),(n,'grounded tree or shared feature')
 assert all(q.distance(other)>=.75-1e-5 for name,other in polys.items() if name!=n),(n,'neighbor')
 l['center']=[round(before[0]+dx,5),round(before[1]+dy,5)];l['angle']=angle;l['lot']=list(translate(rotate(Polygon(l['lot']),turn*180/math.pi,origin=before),dx,dy).exterior.coords)[:-1]
 if plaza:l['plazaFacing']=True;l.pop('courtyard',None)
 polys[n]=q;moves.append({'id':n,'before':before,'after':l['center'],'rotation':turn,'plazaFacing':plaza})
# Preserve the street-facing neighboring modules while making room for the
# south square frontage's full roof/awning envelope, without reducing streets.
move('district-northwest-lodge',lots['district-northwest-lodge']['angle'],-.6,0)
for n in ('capital-workshop-057','capital-market-072'):move(n,lots[n]['angle'],0,1.2)
selected=[('capital-neighborhood-024',0),('district-west-courtyard-home',0),('ro3-infill-approach-1',0),('capital-residential-044-b',0),('capital-residential-040-b',-math.pi/2),('capital-residential-052-b',-math.pi/2),('capital-residential-028-b',math.pi/2),('capital-workshop-032-b',math.pi/2),('capital-residential-058-a',math.pi),('capital-workshop-034-a',math.pi)]
offsets=sorted([(i*.1,j*.1) for i in range(-20,21) for j in range(-20,21)],key=lambda q:q[0]**2+q[1]**2)
for n,angle in selected:
 for dx,dy in offsets:
  try:move(n,angle,dx,dy,True);break
  except AssertionError:continue
 else:raise AssertionError(('No clear plaza-facing placement',n))
for c in p['courtyards']:c['homes']=[n for n in c['homes'] if not lots[n].get('plazaFacing')]
p['plazaFrontageRefinement']={'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'moves':moves,'trees':tree_moves,'streetFurniture':furniture_moves,'frontages':[n for n,a in selected],'squareCenter':[128,144],'completeModelsPreserved':True,'publicStreetWidthsUnchanged':True}
(O/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print('PLAZA FRONTAGES',len(selected),'whole models moved',len(moves));print(json.dumps(moves))
