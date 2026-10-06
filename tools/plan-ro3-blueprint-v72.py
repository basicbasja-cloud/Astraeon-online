"""Plan a larger symmetric town heart and closed, owned building-zone boundaries.

Uses Shapely2.1.2 offline; the resulting plan is authored into native Blender.
"""
import argparse,json,math,runpy
from pathlib import Path
from shapely.geometry import Polygon,box,Point,MultiPolygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
ROOT=Path(__file__).resolve().parents[1];h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'))
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();w=json.loads(args.source.read_text())
ornamentMoves={name:[0,-.35,0] for name in ('plaza-herald-west-north','plaza-herald-east-north','plaza-herald-west-south','plaza-herald-east-south')}
moves={'frontage-bookbinder':[2,-.8,0],'inn-side-home':[0,4.5,0],'frontage-baker':[-.5,-.5,0],'frontage-apothecary':[3,6.0,0],'ro3-infill-approach-1':[1.5,3.2,0]}
houses=[]
objects={o['id']:o for o in w['objects']}
architectureChanges={}
for p in objects['civic-terrace-retaining']['parts']:
 name=p['id']
 if '(8, 0)' in name:architectureChanges[name]={'mode':'scaleX','anchor':65.4,'factor':5.85/7.4}
 elif '(12, 0)' in name:architectureChanges[name]={'mode':'scaleX','anchor':42.6,'factor':5.85/7.4}
 elif '(9, 0' in name:architectureChanges[name]={'mode':'offsetX','offset':1.55}
 elif '(11, 0' in name:architectureChanges[name]={'mode':'offsetX','offset':-1.55}
 elif '(8, 0,' in name:architectureChanges[name]={'mode':'offsetX','offset':{0:0,1:.775,2:1.55}[int(name.split(',')[-1].strip(' )'))]}
 elif '(12, 0,' in name:architectureChanges[name]={'mode':'offsetX','offset':{0:-1.55,1:-.775,2:0}[int(name.split(',')[-1].strip(' )'))]}
def point(p,v):
 x,y=v[:2];a=architectureChanges.get(p['id'])
 if a:x=a['anchor']+(x-a['anchor'])*a['factor'] if a['mode']=='scaleX' else x+a['offset']
 return x,y
def body(o,p):
 d=treeMoves.get(p['id'],moves.get(o['id'],ornamentMoves.get(o['id'],[0,0,0])));return Polygon(h['hull']([[point(p,v)[0]+d[0],point(p,v)[1]+d[1]] for v in p['vertices']]))
ownedSolids=[]
treeMoves={}
for o in w['objects']:
 for p in o['parts']:
  if p['id'].endswith('-ground-core') or p['id'].startswith('side-v59-') and p['id'].endswith('-lower-walls'):
   delta=moves.get(o['id'],[0,0,0]);poly=Polygon(h['hull']([[v[0]+delta[0],v[1]+delta[1]] for v in p['vertices']]));houses.append({'owner':o['id'],'polygon':poly,'kind':'building'})
assert len(houses)==37
for a in houses:a['property']=unary_union([body(objects[a['owner']],p) for p in objects[a['owner']]['parts'] if p['role']=='solid'])
# Civic architecture receives the same closed ownership boundaries.
for name,ids in [('guild-hall',['concept-v49-aisle-foundation--1','concept-v49-nave-foundation','concept-v49-aisle-foundation-1']),('moon-shrine',['moon-shrine-walls'])]:
 o=objects[name];poly=unary_union([body(o,p) for p in o['parts'] if p['id'] in ids]).convex_hull;houses.append({'owner':name,'polygon':poly,'property':unary_union([body(o,p) for p in o['parts'] if p['role']=='solid']),'kind':'civic'})
plaza=box(40,43,68,62.5).buffer(-3).buffer(3,quad_segs=12);oldcourt=next(s for s in w['terrain']['surfaces'] if s['material']=='publicSquareStone');oldarea=Polygon(h['hull'](oldcourt['vertices'])).area;center=[54,52.75]
for house in houses:assert not house['polygon'].intersects(plaza),(house['owner'],'plaza core conflict')
for i,a in enumerate(houses):
 for b in houses[:i]:assert a['polygon'].intersection(b['polygon']).area<.00001,(a['owner'],b['owner'],'house conflict')
roads=[]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
for s in w['terrain']['surfaces']:
 if not(s.get('centerline') and s.get('width',0)>=1.8):continue
 points=s['centerline'];width=s['width'];name=s['id'];new=[];widths=[]
 for x,y in points:
  ww=width
  if 'west-crossroad' in name:
   f=smooth((x-28.54)/(35-28.54));y=y*(1-f)+52.75*f;ww=width*(1-f)+8*f
  elif 'east-crossroad' in name:
   f=1-smooth((x-73)/(80-73));y=y*(1-f)+52.75*f;ww=width*(1-f)+8*f
  elif 'arrival-avenue' in name:
   f=1-smooth((y-66.265)/(72-66.265));x=x*(1-f)+54*f;ww=width*(1-f)+8*f
  elif 'consortium-walk' in name:
   f=smooth((y-37.5)/(39.235-37.5));x=x*(1-f)+54*f;ww=width*(1-f)+8*f
  new.append((x,y));widths.append(ww)
 (ax,ay),(bx,by)=new;length=math.hypot(bx-ax,by-ay);n=(-(by-ay)/length,(bx-ax)/length);q=[(ax+n[0]*widths[0]/2,ay+n[1]*widths[0]/2),(bx+n[0]*widths[1]/2,by+n[1]*widths[1]/2),(bx-n[0]*widths[1]/2,by-n[1]*widths[1]/2),(ax-n[0]*widths[0]/2,ay-n[1]*widths[0]/2)];roads.append({'id':name,'polygon':Polygon(q),'major':width>=3.6,'centerline':new,'widths':widths,'z':min(v[2] for v in s['vertices'])})
# Exact reflected approaches meet the rounded court; district bends start farther out.
approaches={'west':box(36,48.75,40,56.75),'east':box(68,48.75,72,56.75),'north':box(50,39.235,58,43),'south':box(50,62.5,58,66.265)}
main=unary_union([plaza,*approaches.values(),*[r['polygon'] for r in roads if r['major']]])
for house in houses:assert house['polygon'].intersection(main).area<.001,(house['owner'],'major public path conflict')
# Trees displaced by the revised streets move as complete rooted groups.
occupied=unary_union([body(o,p) for o in w['objects'] for p in o['parts'] if p['role']=='solid']);land0=Polygon(w['terrain']['walkablePolygon']);treeTargets=[];treeLand=land0.buffer(-1);treePublic=main.buffer(1.15);treeOccupied=occupied.buffer(1.3)
for o in w['objects']:
 if o['family']!='vegetation':continue
 for p in o['parts']:
  if p['role']!='solid':continue
  shape=body(o,p)
  if shape.intersection(main.buffer(.45)).area<.00001:continue
  old=shape.centroid;candidates=[]
  for ix in range(-30,31):
   for iy in range(-30,31):
    q=Point(old.x+ix*.45,old.y+iy*.45)
    if not treeLand.covers(q) or treePublic.covers(q) or treeOccupied.covers(q):continue
    if any(q.distance(a)<2.5 for a in treeTargets):continue
    houseDistance=min(q.distance(a['polygon']) for a in houses)
    if houseDistance>3.3:continue
    candidates.append((old.distance(q)+.2*houseDistance,q))
  assert candidates,('No rooted tree margin',p['id'])
  _,q=min(candidates,key=lambda a:a[0]);treeMoves[p['id']]=[q.x-old.x,q.y-old.y,0];treeTargets.append(q)
# Historical district roads respect occupied props and foundations. New exact
# approaches and the square stay protected; occupied old road margins are trimmed.
fixed=unary_union([body(o,p).buffer(.55) for o in w['objects'] if o['family']!='vegetation' and o['id']!='astral-fountain' for p in o['parts'] if p['role']=='solid'])
islands=[]
for name in ornamentMoves:
 o=objects[name];plinth=next(p for p in o['parts'] if p['role']=='solid');centerPoint=body(o,plinth).centroid;islands.append({'id':'herald-island-'+name,'owners':[name],'polygon':centerPoint.buffer(1.15,quad_segs=16),'kind':'civic-planting'})
islandMask=unary_union([z['polygon'] for z in islands]);courtPaving=plaza.difference(islandMask)
for r in roads:r['polygon']=r['polygon'].difference(fixed).difference(islandMask)
stairReserve=box(49.25,34.65,58.75,41.45)
main=unary_union([courtPaving,stairReserve,*approaches.values(),*[r['polygon'] for r in roads if r['major']]])
land=Polygon(w['terrain']['walkablePolygon'])
# Shared plots join adjoining frontages. Their edges are native closed polygons,
# rather than independently terminated road strips. Public court and main ways
# remain fixed; minor walks flow around the plots.
raw=unary_union([o['property'].buffer(2.3,join_style=2) for o in houses]).intersection(land.buffer(-.12)).difference(main.buffer(.025,join_style=1))
raw=unary_union([raw.buffer(-.55,join_style=1).buffer(.55,join_style=1).intersection(raw),*[o['property'].buffer(.52,join_style=1).difference(main.buffer(.025)) for o in houses]])
# Retaining walls, town walls and other neighboring solids are closed cutouts.
others=unary_union([body(o,p).buffer(.12) for o in w['objects'] if o['id'] not in {a['owner'] for a in houses} and o['family']!='vegetation' for p in o['parts'] if p['role']=='solid'])
protectedBodies=unary_union([a['property'].buffer(.52) for a in houses])
raw=raw.difference(others.difference(protectedBodies)).simplify(.006,preserve_topology=True)
# A shared district plot absorbs built retaining/fence edges encountered at its
# perimeter. Its closed curb goes around the built area, never through a wall.
solids=[body(o,p) for o in w['objects'] if o['id']!='astral-fountain' for p in o['parts'] if p['role']=='solid']
for iteration in range(40):
 band=raw.difference(raw.buffer(-.36));hits=[p for p in solids if p.intersection(band).area>.00001]
 if not hits:break
 new=unary_union([raw,*[p.buffer(.55,join_style=1) for p in hits]]).difference(main.buffer(.025))
 if new.symmetric_difference(raw).area<.00001:break
 raw=new
else:raise AssertionError('Building boundary did not converge')
raw=raw.simplify(.018,preserve_topology=True)
polygons=list(raw.geoms) if raw.geom_type=='MultiPolygon' else [raw]
zones=[]
for poly in polygons:
 owners=[o['owner'] for o in houses if poly.covers(o['polygon'].representative_point())]
 if not owners:continue
 # Curb width requires a meaningful building-side apron, even at narrow corners.
 assert not poly.buffer(-.36).is_empty
 for name in owners:
  bodyPoly=next(o['polygon'] for o in houses if o['owner']==name);assert poly.buffer(.02).covers(bodyPoly),(name,'plot clips house')
 zones.append({'id':'building-zone-'+str(len(zones)),'owners':owners,'polygon':poly,'kind':'building'})
assert set(o['owner'] for o in houses)=={name for z in zones for name in z['owners']}
zones.extend(islands)
private=unary_union([z['polygon'] for z in zones]);publicRoads=[]
for r in roads:
 poly=r['polygon'] if r['major'] else r['polygon'].difference(private.buffer(.02))
 publicRoads.append({**r,'polygon':poly})
def encoded(poly):
 if poly.is_empty:return []
 vals=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
 return [{'outer':list(p.exterior.coords)[:-1],'holes':[list(r.coords)[:-1] for r in p.interiors]} for p in vals if p.geom_type=='Polygon' and p.area>.005]
def mesh(poly):
 triangles=[]
 if not poly.is_empty:
  for t in constrained_delaunay_triangles(poly.segmentize(.60)).geoms:
   if poly.covers(t.representative_point()):triangles.append(list(t.exterior.coords)[:3])
 return triangles
aprons=[]
for a in w['terrain']['surfaces']:
 if not a['id'].startswith('lot69-apron-'):continue
 poly=Polygon(h['hull'](a['vertices']));owner=a.get('objectId') or min(houses,key=lambda z:poly.distance(Polygon(h['hull'](next(p['vertices'] for p in objects[z['owner']]['parts'] if p['id'].endswith('-ground-core') or p['id'].startswith('side-v59-') and p['id'].endswith('-lower-walls')))) ) if z['kind']=='building' else float('inf'))['owner'];d=moves.get(owner,[0,0,0]);poly=Polygon([(x+d[0],y+d[1]) for x,y in poly.exterior.coords]);poly=poly.intersection(private.buffer(-.39));aprons.append({'id':a['id'],'owner':owner,'triangles':mesh(poly),'z':min(v[2] for v in a['vertices'])})
result={'ornamentMoves':ornamentMoves,'architectureChanges':architectureChanges,'stairReserve':encoded(stairReserve),'aprons':aprons,'version':72,'center':center,'plaza':{'bounds':[40,43,68,62.5],'cornerRadius':3,'beforeArea':oldarea,'area':plaza.area,'increasePercent':(plaza.area/oldarea-1)*100,'outline':encoded(courtPaving),'triangles':mesh(courtPaving),'pavedArea':courtPaving.area,'pavedAreaIncreasePercent':(courtPaving.area/oldarea-1)*100},'approaches':{name:{'outline':encoded(p),'triangles':mesh(p),'width':8} for name,p in approaches.items()},'treeMoves':treeMoves,'houseMoves':moves,'ordinaryHouseCount':37,'zones':[{'id':z['id'],'owners':z['owners'],'kind':z['kind'],'area':z['polygon'].area,'outline':encoded(z['polygon']),'triangles':mesh(z['polygon']),'curbWidth':.36,'curbBands':[{'from':a,'to':b,'triangles':mesh(z['polygon'].buffer(-a,join_style=1,quad_segs=4).difference(z['polygon'].buffer(-b,join_style=1,quad_segs=4)))} for a,b in [(0,.035),(.035,.325),(.325,.36)]],'curbInner':encoded(z['polygon'].buffer(-.36,join_style=1,quad_segs=4)),'greenTriangles':mesh(z['polygon'].buffer(-.39).difference(body(objects[z['owners'][0]],next(p for p in objects[z['owners'][0]]['parts'] if p['role']=='solid')).buffer(.045))) if z['kind']=='civic-planting' else []} for z in zones],'roads':[{'id':r['id'],'outline':encoded(r['polygon']),'triangles':mesh(r['polygon']),'z':r['z'],'major':r['major'],'centerline':r['centerline'],'widths':r['widths']} for r in publicRoads],'closedBoundaryLoops':sum(len(z['polygon'].interiors)+1 for z in zones),'rule':'Closed shared building-zone outlines; rounded plaza-facing edges; continuous curb height with lowered entrances; reflected cross approaches; minor walking paths follow plot boundaries'}
for z,r in zip(zones,result['zones']):
 r['curbDistances']={f'{x:.7f},{y:.7f}':z['polygon'].boundary.distance(Point(x,y)) for b in r['curbBands'] for t in b['triangles'] for x,y in t}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'zones':len(zones),'closedLoops':result['closedBoundaryLoops'],'houses':37,'plazaBeforeArea':oldarea,'plazaArea':plaza.area,'increasePercent':result['plaza']['increasePercent'],'treeMoves':treeMoves,'houseMoves':moves}))
