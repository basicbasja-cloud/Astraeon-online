"""Expand selected owned garden pockets from actual paving and use clearances.
No public floor or collision changes. Old lawns are a strict subset of the new
union; only touched blocks are retessellated to remove internal feather seams.
"""
import argparse,json,math,hashlib,runpy,random
from pathlib import Path
from shapely.geometry import Polygon,Point,LineString,MultiPoint
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v79/painted-landscape';O.mkdir(parents=True,exist_ok=True)
ap=argparse.ArgumentParser();ap.add_argument('--baseline-commit',required=True);args=ap.parse_args()
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='67c6ff1f94bdaaa8a278437306beab0b3d94026a106b77e436f93b660dba57d9'
s=json.loads(raw);city=json.loads((R/'docs/review/wayfarer-capital-v78/native-plan.json').read_text());owners={o['id']:o for o in s['objects']}
def region(parts):return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<.0001 for v in a['vertices'])])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.12,cap_style=2,join_style=2) for a in city['roads']])
feet=[];props=[];entries=[]
for o in s['objects']:
 if o['id'] in ('capital-beta-frontage-groundcover','capital-grass-ingress-v76'):continue
 for a in o['parts']:
  if a['role']=='solid' and min(v[2] for v in a['vertices'])<1:feet.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.20))
  if a.get('visible',True) and a['material'] not in ('grass','leaf','flowerRose','vergeGroundcover','vergeGroundcoverShade'):
   low=[v[:2] for v in a['vertices'] if v[2]<1.05]
   if len(low)>=3:props.append(MultiPoint(low).convex_hull.buffer(.12))
for l in city['lots']:
 a=l['angle']+l.get('frontageOffset',0);n=(-math.sin(a),math.cos(a))
 door=next(q for q in owners[l['id']]['parts'] if q['id'].endswith('-door-leaf'));dc=[sum(v[i] for v in door['vertices'])/len(door['vertices']) for i in (0,1)]
 entries.append(LineString([dc,[dc[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
patrols=[LineString(w['route']+[w['route'][0]]).buffer(.38) for o in s['objects'] for w in o.get('walkers',[]) if len(w['route'])>1]
features=[Polygon(a['polygon']).buffer(.3) for a in city.get('courtyards',[])]+[Point(a['position'][:2]).buffer(1.2) for o in s['objects'] for a in o.get('services',[])]+[Point(a['anchor'][:2]).buffer(1.2) for o in s['objects'] for a in o.get('portals',[])]
keepout=unary_union(feet+props+entries+patrols+features+[roads])
focus=[{'name':'Artisan homes','center':[68,168],'radius':10},{'name':'West neighborhood','center':[68,201],'radius':8},{'name':'Merchant property','center':[48,165],'radius':10},{'name':'Willow residences','center':[153,200],'radius':8},{'name':'Borough homes','center':[176,224],'radius':8},{'name':'South residences','center':[108,222],'radius':7}]
focus_zone=unary_union([Point(a['center']).buffer(a['radius']) for a in focus])
oldparts=owners['capital-beta-frontage-groundcover']['parts'];oldgreen=region(oldparts);oldzones={a['id']:region([a]) for a in oldparts};pieces=[];replaced=[];additions=[];blocks=[]
for index,b in enumerate(city['ownedBlocks']):
 block=Polygon(b['outer'],b['holes'])
 if not block.intersects(focus_zone):continue
 prior=[a for a in oldparts if block.buffer(.0002).covers(oldzones[a['id']])]
 if not prior:continue
 prior_zone=region(prior)
 # Grow the planted pockets inward by a bounded95cm. Keep the reviewed outer
 # curb setback; use the current real floor union rather than a cached lot box.
 extra=prior_zone.buffer(.95,quad_segs=4).intersection(block.buffer(-.18,join_style=2)).intersection(private).difference(keepout).difference(oldgreen)
 extra=extra.simplify(.045,preserve_topology=True).intersection(private).difference(keepout).difference(oldgreen)
 if extra.area<3:continue
 joined=prior_zone.union(extra);polys=[joined] if joined.geom_type=='Polygon' else list(joined.geoms)
 for q in polys:
  if q.geom_type!='Polygon' or q.area<.01:continue
  vertices=[];faces=[]
  for t in constrained_delaunay_triangles(q).geoms:
   assert q.covers(t)
   pts=list(t.exterior.coords)[:-1]
   if not t.exterior.is_ccw:pts.reverse()
   off=len(vertices);vertices.extend([[x,y,.047] for x,y in pts]);faces.append([off,off+1,off+2])
  pieces.append({'id':f'painted-property-lawn-v79-{index:02}-{len(pieces):03}','block':index,'vertices':vertices,'faces':faces,'material':'grass','area':q.area})
 replaced.extend(a['id'] for a in prior);additions.append(extra);blocks.append({'block':index,'addedArea':extra.area,'beforeArea':prior_zone.area,'afterArea':joined.area})
extra_union=unary_union(additions);assert 60<extra_union.area<650,extra_union.area
plan={'pieces':pieces};feather=runpy.run_path(str(R/'tools/plan-capital-grass-feather-v76.py'))['feather_plan'];f=feather(plan)
old_tri=sum(len(a['faces']) for a in oldparts if a['id'] in replaced);added_tri=f['triangles']-old_tri;assert added_tri<16000
# Sparse actual geometry at new planted edges. Original1200 roots remain exact.
rng=random.Random(79079);roots=[];zones=extra_union.buffer(-.13);bounds=extra_union.bounds;target=min(240,int(extra_union.area*.6))
for attempt in range(target*100):
 if len(roots)>=target:break
 q=Point(rng.uniform(bounds[0],bounds[2]),rng.uniform(bounds[1],bounds[3]))
 if not zones.covers(q) or extra_union.boundary.distance(q)>.75 or any(q.distance(Point(a['position'][:2]))<.30 for a in roots):continue
 roots.append({'position':[q.x,q.y,.059],'height':rng.uniform(.05,.095),'width':rng.uniform(.018,.032),'angle':rng.uniform(0,math.tau)})
assert len(roots)>25,len(roots)
images={m['texture']['file'] for m in s['materials'].values() if m.get('texture')}
report={'baselineCommit':args.baseline_commit,'beforeSourceSHA256':sha,'focusAreas':focus,'replacedLawnParts':replaced,'blocks':blocks,
 'beforeTotalLawnArea':oldgreen.area,'addedLawnArea':extra_union.area,'afterTotalLawnArea':oldgreen.area+extra_union.area,
 'pieces':f['pieces'],'lawnAddedTriangles':added_tri,'grassRoots':roots,'grassOwner':'capital-painted-garden-blades-v79','grassTriangleBudget':1000,
 'formalTrees':[f'capital-tree-{i:03}' for i in list(range(8))+list(range(16,24))],
 'newFoliageMetadata':'authoring/materials/wayfarer-conifer-v79.json','entranceClearWidth':2.2,'additionalImageAssets':1,
 'materialColors':{'roofClayWarm':[.66,.32,.18],'roofClayRose':[.58,.25,.17],'roofClayOchre':[.64,.38,.23]},
 'originalImages':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in images},'existingTerrainCollisionGameplayUnchanged':True,
 'strategy':'Grow selected actual owned green pockets inward; keep courts, work bays, public paving and closed patrols clear; distinct formal crowns and broad painted foliage clusters',
 'visualAcceptance':'Pending source-matched gameplay comparison'}
(O/'plan.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('pieces','grassRoots','originalImages','replacedLawnParts','blocks')},indent=2));print('Touched blocks',len(blocks),'new sparse roots',len(roots),'new lawn triangles',added_tri)
