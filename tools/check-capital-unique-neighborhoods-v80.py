"""Independent scoped v79/v80 preservation and actual-placement proof."""
import json,hashlib,math,subprocess,collections,argparse
from pathlib import Path
from shapely.geometry import Point,Polygon,MultiPoint,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v80/unique-neighborhoods';A=R/'docs/review/wayfarer-capital-v79/painted-landscape'
ap=argparse.ArgumentParser();ap.add_argument('--pending-light',action='store_true');args=ap.parse_args()
p=json.loads((O/'plan.json').read_text());receipt=json.loads((O/'authoring.json').read_text());garden=json.loads((A/'plan.json').read_text());gr=json.loads((A/'authoring.json').read_text());layout=json.loads((O.parent/'native-plan.json').read_text())
def read(path):return json.loads(path.read_bytes())
import runpy
helpers=runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'));fingerprint=helpers['fingerprint'];unlit=helpers['unlit'];metadata=helpers['metadata'];facekeys=helpers['facekeys'];baseline=read(O/'authored-landscape-baseline.json');assert baseline['v79Pass'] and baseline['beforeSourceSHA256']==p['beforeSourceSHA256']
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw);now={a['id']:a for a in s['objects']};added={a['id'] for a in p['trees']};changed={a['id'] for a in p['houses']}
assert set(now)-set(baseline['owners'])==added and not set(baseline['owners'])-set(now)
retainedlow=0
for n,entry in baseline['owners'].items():
 o=now[n];assert fingerprint(metadata(o))==entry['metadata'],(n,'gameplay changed')
 if n not in changed:assert fingerprint([unlit(a) for a in o['parts']])==entry['parts'],(n,'undeclared geometry/UV/normal change')
 else:
  parts={a['id']:a for a in o['parts']}
  for name,sha in entry['retainedParts'].items():assert fingerprint(unlit(parts[name]))==sha,(n,name,'retained core/door/shelter')
  low=collections.Counter(entry['groundFaces']);assert not low-facekeys(o),(n,'old ground frontage disappeared');retainedlow+=sum(low.values())
assert fingerprint(s['materials'])==baseline['materials']
assert fingerprint({k:v for k,v in s.items() if k not in ('objects','materials','lighting')})==baseline['common']
assert fingerprint({k:v for k,v in s['lighting'].items() if k!='groundShadow'})==baseline['lighting']
if not args.pending_light:assert s['lighting']['groundShadow']['file']=='assets/wayfarer-ground-shadow-v80-neighborhoods.png' and s['lighting']['groundShadow']['resolution']==4096
for image,sha in garden['originalImages'].items():assert hashlib.sha256((R/image).read_bytes()).hexdigest()==sha,image
art=read(R/'authoring/materials/wayfarer-conifer-v79.json');assert art['losslessRGBAExact'] and hashlib.sha256((R/art['texture']['file']).read_bytes()).hexdigest()==art['assetSHA256']
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2,cap_style=2,join_style=2) for a in layout['roads']]);solids=unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull for o in now.values() if o['id'] not in added for a in o['parts'] if a['role']=='solid']);patrols=unary_union([LineString(w['route']+[w['route'][0]]).buffer(.45) for o in s['objects'] for w in o.get('walkers',[]) if len(w['route'])>1])
green=unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in now['capital-beta-frontage-groundcover']['parts'] for f in a['faces']]+[Polygon(a['polygon']) for a in layout['parks']]);entries=[]
for l in layout['lots']:
 door=next(a for a in now[l['id']]['parts'] if a['id'].endswith('-door-leaf'));dc=[sum(v[i] for v in door['vertices'])/len(door['vertices']) for i in (0,1)];normal=(-math.sin(l['angle']),math.cos(l['angle']));entries.append(LineString([dc,[dc[i]+normal[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
entryzone=unary_union(entries);treeproof=[]
roofzone=unary_union([MultiPoint([v[:2] for a in o['parts'] if a['role']=='overhead' for v in a['vertices']]).convex_hull for o in now.values() if o['family']!='vegetation' and any(a['role']=='overhead' for a in o['parts'])])
oldcrowns=unary_union([MultiPoint([v[:2] for a in o['parts'] for v in a['vertices']]).convex_hull for o in now.values() if o['id'] not in added and o['family']=='vegetation' and any(a['role']=='solid' for a in o['parts'])])

for a in p['trees']:
 o=now[a['id']];stem=next(v for v in o['parts'] if v['role']=='solid');foot=MultiPoint([v[:2] for v in stem['vertices']]).convex_hull;q=Point(a['position'][:2]);assert green.covers(q.buffer(.21))
 assert not foot.intersects(roads) and not foot.intersects(solids) and not foot.intersects(patrols) and not foot.intersects(entryzone),a['id']
 assert abs(min(v[2] for v in stem['vertices'])-(a['position'][2]-.015))<.00003,a['id']
 leafvs=[v for part in o['parts'] if part['material'].startswith('conifer70') for v in part['vertices']];assert max(math.dist(v[:2],a['position'][:2]) for v in leafvs)<a['radiusBudget']+.025
 crown=MultiPoint([v[:2] for v in leafvs]).convex_hull;assert not crown.intersects(roofzone) and not crown.intersects(oldcrowns),a['id']
 assert all(math.dist(a['position'][:2],b['position'][:2])>2.7 for b in p['trees'] if b['id']!=a['id'])
 treeproof.append({'id':a['id'],'plantedGround':True,'entranceStreetPatrolClear':True,'height':a['height'],'zone':a['zone']})
dormerproof=[]
for spec in p['houses']:
 if spec['design'] not in ('garden-cottage','dormered-gambrel'):continue
 c,sn=math.cos(spec['angle']),math.sin(spec['angle']);cx,cy=spec['center'];d=spec['depth'];top=(4.6 if spec['design']=='garden-cottage' else 5.2)+spec['variation'];gambrel=spec['design']=='dormered-gambrel';eave=top+(.16 if gambrel else .14);b=d/2+(.28 if gambrel else .2)
 windows=[a for a in now[spec['id']]['parts'] if a['material']=='frontageGlazing' and a['id'].startswith('capital-v80-') and 'dormer' in a['id']];assert windows,spec['id'];clearance=100
 for part in windows:
  for v in part['vertices']:
   y=-(v[0]-cx)*sn+(v[1]-cy)*c;z=v[2]-.04
   roofheight=eave+1.8*(b-abs(y))/(b-b*.45) if gambrel and abs(y)>=b*.45 else eave+2.65-.85*abs(y)/(b*.45) if gambrel else eave+2.05*(1-abs(y)/b)
   clearance=min(clearance,z-roofheight)
 assert clearance>.05,(spec['id'],'dormer glazing buried in main roof',clearance)
 dormerproof.append({'id':spec['id'],'exposedWindows':len(windows),'minimumRoofClearance':clearance})
assert len({a['design'] for a in p['houses']})==4 and len(changed)==12
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'pass':True,'lightingVerified':not args.pending_light,'v79OriginalPartsExactOutsideDeclaredGardensCrowns':baseline['v79OriginalPartsExactOutsideDeclaredGardensCrowns'],'v80PreservedGroundFrontageFaces':retainedlow,'structuralHouses':12,'exposedDormerWindows':dormerproof,'uniqueStructuralDesigns':4,'allOriginal84TreeRootsAndGeometryAfterV79Exact':True,'treePlacements':treeproof,'originalCoreDoorsSheltersTerrainNavigationGameplayExact':True,'originalImagesAndResolutionExact':True,'visualAcceptance':'Requires source-matched gameplay inspection'}
(O/('geometry-candidate.json' if args.pending_light else 'declared-delta.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
