"""Independent source74 assembly preservation and capital geometry review.

Uses the committed source74 export, compares every retained vertex and original
UV corner, and measures native face unions rather than unordered vertex lists.
"""
import json,math,subprocess,hashlib,os
from pathlib import Path
from shapely.geometry import Polygon,LineString,MultiPoint,Point
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];out=ROOT/os.environ.get('ASTRAEON_CAPITAL_REVIEW_DIR','docs/review/wayfarer-capital-v75');p=json.loads((out/'native-plan.json').read_text());s=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());old=json.loads(subprocess.check_output(['git','show','7b72b3f:world/v3/wayfarer-spatial.json'],cwd=ROOT));objects={o['id']:o for o in s['objects']};max_error=0;vertices=0;uvfaces=0
for o in old['objects']:
 t=p['transforms'].get(o['id'])
 if not t:continue
 current={m['id']:m for m in objects[o['id']]['parts']};a=math.cos(t['rotation']);b=math.sin(t['rotation']);bx,by,bz=t['before'];ax,ay,az=t['after']
 for m in o['parts']:
  n=current[m['id']];assert n['faces']==m['faces'],m['id']
  if 'uvs' in m:assert n['uvs']==m['uvs'],m['id']+' original UV';uvfaces+=len(m['faces'])
  assert len(n['vertices'])==len(m['vertices'])
  for v,q in zip(m['vertices'],n['vertices']):
   expected=[ax+a*(v[0]-bx)-b*(v[1]-by),ay+b*(v[0]-bx)+a*(v[1]-by),az+v[2]-bz];error=max(abs(x-y) for x,y in zip(expected,q));max_error=max(max_error,error);assert error<.0002,(m['id'],error);vertices+=1
house_ids=[l['id'] for l in p['lots']];assert len(house_ids)==len(set(house_ids))==p['existingHouses']+p['newHouses']
assert all(n in objects for n in house_ids)
services=[a for o in s['objects'] for a in o.get('services',[])];assert sorted(a['id'] for a in services)==sorted(a['id'] for o in old['objects'] for a in o.get('services',[]))
portals=[a for o in s['objects'] for a in o['portals'] if a.get('transition')];assert len(portals)==2
assert sorted((a['id'],a['transition']['to']) for a in portals)==sorted((a['id'],a['transition']['to']) for o in old['objects'] for a in o['portals'] if a.get('transition'))
floors=s['terrain']['surfaces'];public=[a for a in floors if a['id'].startswith('capital-public-') or a['id']=='capital-royal-plaza'];private=[a for a in floors if a['id'].startswith('capital-private-')]
street_scale=None
if p.get('ro3StreetScaleRefinement'):
 revision=p['ro3StreetScaleRefinement'];native_roads={a['id']:a for a in floors if a.get('centerline')}
 for road in p['roads']:
  assert road['width']>=8,('public street below the reviewed scale',road['id'])
  for j,(a,b) in enumerate(zip(road['centerline'],road['centerline'][1:])):
   native=native_roads[road['id']+'-'+str(j)];assert native['centerline']==[a,b] and native['width']==road['width']
   expected=LineString([a,b]).buffer(road['width']/2,cap_style=2)
   assert Polygon(native['polygon']).symmetric_difference(expected).area<.001,('street polygon does not match its width',native['id'])
 assert not any(any(name.startswith(removed+'-') for removed in revision['removedThroughLanes']) for name in native_roads)
 public_segments=sum(len(r['centerline'])-1 for r in p['roads'])
 street_scale={'roadObjects':len(p['roads']),'nativePublicSegments':public_segments,'retainedGardenFootpaths':len(native_roads)-public_segments,'minimumPublicWidth':min(r['width'] for r in p['roads']),'districtWidth':9,'circuitWidth':10,'removedThroughLanes':revision['removedThroughLanes'],'nativeWidthsAndPolygonsMatch':True}
def region(arr):return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in arr for f in a['faces']])
public_region=region(public);private_region=region(private);overlap=public_region.intersection(private_region).area;assert overlap<.001
public_uv_size=p.get('betaReferenceRefinement',{}).get('publicStoneWorldSize',8)
assert public_uv_size in (8,3.2)
assert s['materials']['publicTownStone']['texture']['worldSize']==public_uv_size
for a in public:
 for f,uvs in zip(a['faces'],a['uvs']):
  for i,uv in zip(f,uvs):assert max(abs(uv[j]-a['vertices'][i][j]/public_uv_size) for j in (0,1))<.00002
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2,cap_style=2,join_style=2) for a in p['roads']])
park_road_overlap=unary_union([Polygon(a['polygon']) for a in p['parks']]).intersection(roads).area
assert park_road_overlap<.001,('garden interrupts avenue',park_road_overlap)
court_checks=[]
for court in p.get('courtyards',[]):
 zone=Polygon(court['polygon']);feature=objects['capital-'+court['id']]
 assert zone.intersection(roads).area<.001,('owned court interrupts street',court['id'])
 for part in feature['parts']:
  assert zone.buffer(.0001).covers(MultiPoint([v[:2] for v in part['vertices']])),('court feature leaves its owned zone',part['id'])
 for name in court['homes']:
  lot=next(l for l in p['lots'] if l['id']==name);dx=court['center'][0]-lot['center'][0];dy=court['center'][1]-lot['center'][1]
  assert -math.sin(lot['angle'])*dx+math.cos(lot['angle'])*dy>0,('frontage faces away from its court',name)
 court_checks.append({'id':court['id'],'inwardFrontages':len(court['homes']),'featuresInsideOwnedZone':True})
plaza_frontages=[]
if p.get('plazaFrontageRefinement'):
 for name in p['plazaFrontageRefinement']['frontages']:
  lot=next(l for l in p['lots'] if l['id']==name);dx=128-lot['center'][0];dy=144-lot['center'][1]
  heading=lot['angle']+lot.get('frontageOffset',0)
  assert -math.sin(heading)*dx+math.cos(heading)*dy>0,('frontage faces away from the square',name)
  # The legacy infill's root heading did not describe its geometric door.
  # Measure the thin horizontal axis of the actual leaf instead of trusting it.
  door=next(a for a in objects[name]['parts'] if a['id'].endswith('-door-leaf'))
  vs=door['vertices']
  extent=[max(v[i] for v in vs)-min(v[i] for v in vs) for i in range(2)]
  center=[sum(v[i] for v in vs)/len(vs) for i in range(2)]
  axis=0 if extent[0]<extent[1] else 1
  assert extent[axis]<extent[1-axis]/3,('door has no clear frontage plane',name)
  normal=[0,0];normal[axis]=1 if center[axis]>lot['center'][axis] else -1
  expected=[-math.sin(heading),math.cos(heading)]
  assert sum(normal[i]*expected[i] for i in range(2))>.999,('actual door direction differs from planned plaza frontage',name,normal,expected)
  plaza_frontages.append(name)
physical=[]
for owner in s['objects']:
 if owner['family']=='vegetation':continue
 for part in owner['parts']:
  if part['role']=='solid':physical.append((owner['id'],MultiPoint([v[:2] for v in part['vertices']]).convex_hull))
floor_faces=[]
for a in floors:
 if not a['walkable']:continue
 for f in a['faces']:
  vs=[a['vertices'][i] for i in f];poly=Polygon([v[:2] for v in vs])
  if poly.area>.000001:floor_faces.append((poly.bounds,poly,max(v[2] for v in vs)))
tree_checks=[];tree_errors=[]
for owner in s['objects']:
 if owner['family']!='vegetation':continue
 if owner['id']=='capital-beta-frontage-groundcover':
  assert p.get('betaReferenceRefinement')
  assert all(a['role']=='decorative' and not a.get('shadow') and a['material']=='grass' and all(abs(v[2]-.047)<.00001 for v in a['vertices']) for a in owner['parts'])
  continue
 trunk=next(a for a in owner['parts'] if a['role']=='solid');poly=MultiPoint([v[:2] for v in trunk['vertices']]).convex_hull
 bounds=poly.bounds
 conflicts={name for name,body in physical if body.bounds[0]<bounds[2] and body.bounds[2]>bounds[0] and body.bounds[1]<bounds[3] and body.bounds[3]>bounds[1] and poly.intersection(body).area>.005}
 if conflicts:tree_errors.append((owner['id'],sorted(conflicts)))
 if poly.intersection(roads).area>=.005:tree_errors.append((owner['id'],'trunk in avenue'))
 x,y=poly.centroid.x,poly.centroid.y;point=Point(x,y);height=max([0]+[z for bounds,body,z in floor_faces if bounds[0]<=x<=bounds[2] and bounds[1]<=y<=bounds[3] and body.covers(point)])
 embed=height-min(v[2] for v in trunk['vertices'])
 if abs(embed-.015)>=.00004:tree_errors.append((owner['id'],'root embed',embed))
 tree_checks.append({'id':owner['id'],'rootEmbed':embed})
assert len(tree_checks)==78,len(tree_checks)
assert not tree_errors,tree_errors
land=Polygon(p['land']);cliff_faces=0;foam_faces=0
for owner in s['objects']:
 if owner['id'] not in ('capital-river-bank','capital-waterline'):continue
 for part in owner['parts']:
  for face in part['faces']:
   a,b,c=[part['vertices'][i] for i in face[:3]];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
   if owner['id']=='capital-waterline':assert normal[2]>0,part['id'];foam_faces+=1;continue
   center=Point(sum(part['vertices'][i][0] for i in face)/len(face),sum(part['vertices'][i][1] for i in face)/len(face));edge=land.boundary.interpolate(land.boundary.project(center));outward=[center.x-edge.x,center.y-edge.y]
   assert normal[0]*outward[0]+normal[1]*outward[1]>0,('inward cliff face',part['id']);cliff_faces+=1
assert cliff_faces>800 and foam_faces>200,(cliff_faces,foam_faces)
curb_faces=0
if p.get('neighborhoodRefinement'):
 parts={a['id']:a for a in objects['capital-owned-block-boundaries']['parts']}
 for i,loop in enumerate(p['privateLoops']):
  for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
   dx,dy=b[0]-a[0],b[1]-a[1]
   if math.hypot(dx,dy)<.0001:continue
   part=parts[f'capital-v75-owned-curb-{i}-{j}'];face=part['faces'][0];v0,v1,v2=[part['vertices'][k] for k in face[:3]];u=[v1[k]-v0[k] for k in range(3)];v=[v2[k]-v0[k] for k in range(3)];nx,ny=u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2]
   assert nx*dy-ny*dx>0,('curb face points into owned block',part['id']);curb_faces+=1
report={'layout':s['layoutId'],'houses':len(house_ids),'existingHouses':37,'newHouses':p['newHouses'],'landmarks':len(p['landmarks']),'preservedAssemblyVertices':vertices,'preservedUVFaces':uvfaces,'maximumTransformError':max_error,'publicPrivateOverlapArea':overlap,'serviceIDsPreserved':len(services),'transitionIDsPreserved':len(portals),'treeCount':len(tree_checks),'treeRootAndSolidClearance':True,'gardenRoadOverlapArea':park_road_overlap,'outwardCliffFaces':cliff_faces,'upwardWaterlineFaces':foam_faces,'outwardOwnedCurbFaces':curb_faces,'sharedOwnedBlocks':len(p.get('ownedBlocks',[])),'pass':True}
if street_scale:report['streetScale']=street_scale
if court_checks:report['courtyards']=court_checks
if plaza_frontages:report['plazaFacingFrontages']=plaza_frontages;report['actualPlazaDoorDirectionsVerified']=True
report['sourceSHA256']=hashlib.sha256((ROOT/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()
(out/'assembly-and-floor-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
