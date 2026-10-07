"""Select original house massing and irregular planting against actual geometry."""
import json,hashlib,math
from pathlib import Path
from shapely.geometry import Polygon,Point,LineString,MultiPoint
from shapely.ops import unary_union
from shapely.prepared import prep
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v80/unique-neighborhoods';O.mkdir(parents=True,exist_ok=True)
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw);p=json.loads((R/'docs/review/wayfarer-capital-v79/native-plan.json').read_text());owners={a['id']:a for a in s['objects']}
choices=[('capital-townhouse-083','stepped-gables',-.18),('capital-townhouse-085','dormered-gambrel',.12),('capital-townhouse-089','corner-oriel',-.1),('capital-residential-073-a','garden-cottage',.12),('capital-residential-076-b','stepped-gables',.15),('capital-market-060','dormered-gambrel',-.18),('capital-market-063','stepped-gables',.12),('capital-residential-040-b','corner-oriel',.1),('capital-residential-028-b','stepped-gables',-.1),('capital-residential-052-b','garden-cottage',-.12),('capital-workshop-032-b','dormered-gambrel',.12),('capital-residential-058-a','garden-cottage',.08)]
houses=[]
for n,kind,variation in choices:
 l=next(a for a in p['lots'] if a['id']==n);assert not l['existing'];houses.append({'id':n,'design':kind,'variation':variation,'center':l['center'],'width':l['width'],'depth':l['depth'],'clay':l['clay'],'family':l['family'],'angle':l['angle'],'preserveDoorCoreFoundationAndShelters':True})
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.3,cap_style=2,join_style=2) for a in p['roads']])
solids=[];low=[];entries=[];oldtrees=[]
for o in s['objects']:
 for a in o['parts']:
  if a['role']=='solid':solids.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull)
  if o['family']=='vegetation' or a['material'] in ('grass','leaf','flowerRose','vergeGroundcover','vergeGroundcoverShade'):continue
  vs=[v[:2] for v in a['vertices'] if v[2]<1.1]
  if len(vs)>=3:low.append(MultiPoint(vs).convex_hull.buffer(.12))
 if o['family']=='vegetation' and any(a['role']=='solid' for a in o['parts']):
  vs=[v[:2] for a in o['parts'] for v in a['vertices']];oldtrees.append(MultiPoint(vs).convex_hull.buffer(.25))
for l in p['lots']:
 door=next(a for a in owners[l['id']]['parts'] if a['id'].endswith('-door-leaf'));q=[sum(v[i] for v in door['vertices'])/len(door['vertices']) for i in (0,1)];n=(-math.sin(l['angle']),math.cos(l['angle']));entries.append(LineString([q,[q[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
patrol=[LineString(w['route']+[w['route'][0]]).buffer(.45) for o in s['objects'] for w in o.get('walkers',[]) if len(w['route'])>1]
features=[Point(a['position'][:2]).buffer(1.2) for o in s['objects'] for a in o.get('services',[])]+[Point(a['anchor'][:2]).buffer(1.2) for o in s['objects'] for a in o.get('portals',[])]+[Polygon(a['polygon']).buffer(.2) for a in p['courtyards']]
green=unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in owners['capital-beta-frontage-groundcover']['parts'] for f in a['faces']]+[Polygon(a['polygon']) for a in p['parks']])
blocked=unary_union(solids+low+entries+patrol+features+[roads]);solidzone=unary_union(solids)
# Roots sit inside actual planted ground; crowns avoid roofs/neighboring trees.
roofs=unary_union([MultiPoint([v[:2] for a in o['parts'] if a['role']=='overhead' for v in a['vertices']]).convex_hull for o in s['objects'] if any(a['role']=='overhead' for a in o['parts'])])
greeninside=prep(green.buffer(-.22));rootblocked=prep(blocked.buffer(.22));crownblocked=prep(unary_union([roofs.buffer(.87)]+[a.buffer(.85) for a in oldtrees]));floorfaces=[(Polygon([a['vertices'][i][:2] for i in f]),max(a['vertices'][i][2] for i in f)) for a in s['terrain']['surfaces'] if a['walkable'] for f in a['faces']];floorfaces=[(a.bounds,a,z) for a,z in floorfaces]
trees=[];attempts=[]
focus=[('west-property',[70,198],2),('court-edge',[96,203],2),('willow-property',[157,198],2),('borough-garden',[176,223],2),('west-common',[64,127],3)]
for label,center,count in focus:
 candidates=[]
 for ix in range(-40,41):
  for iy in range(-40,41):
   x,y=center[0]+ix*.25,center[1]+iy*.25;q=Point(x,y)
   if not greeninside.covers(q) or rootblocked.intersects(q):continue
   if crownblocked.intersects(q):continue
   candidates.append((q.distance(Point(center)),x,y))
 picked=0
 for score,x,y in sorted(candidates):
  if picked>=count:break
  if any(math.dist([x,y],a['position'][:2])<2.8 for a in trees):continue
  # Actual highest walkable contact under each declared root.
  z=max([0]+[z for bounds,a,z in floorfaces if bounds[0]<=x<=bounds[2] and bounds[1]<=y<=bounds[3] and a.covers(Point(x,y))])
  n=len(trees);trees.append({'id':f'capital-garden-tree-v80-{n:02}','zone':label,'position':[x,y,z],'height':3.1+(n%3)*.35,'rotation':(n*2.399963)%math.tau,'crown':'rounded' if n%3!=1 else 'upright','radiusBudget':.85});picked+=1
 attempts.append({'zone':label,'requested':count,'placed':picked})
assert len(trees)>=6,(len(trees),attempts)
plan={'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'houses':houses,'trees':trees,'plantingZones':attempts,'houseDesigns':4,'triangleBudget':18000,'treeTriangleBudget':15000,'originalGroundNavigationAndGameplayRetained':True,'entranceClearWidth':2.2,'placementPolicy':'Informal property/garden clusters with varied height/rotation; retain symmetrical royal parterres and avenues. Root in planted ground; crowns and routes clear.','referencePolicy':'RO3 proportions, painted material tone and occupied property adjacency; original Astraeon geometry, no copied assets.'}
(O/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({k:v for k,v in plan.items() if k!='houses'},indent=2))
