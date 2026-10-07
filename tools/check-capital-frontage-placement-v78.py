"""Independent declared-delta, actual placement and original-image audit."""
import json,hashlib,subprocess,math
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint,LineString,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v78/frontage-placement'
p=json.loads((O/'plan.json').read_text());r=json.loads((O/'authoring.json').read_text());layout=json.loads((O.parent/'native-plan.json').read_text())
oldraw=subprocess.check_output(['git','show',p['baselineCommit']+':world/v3/wayfarer-spatial.json'],cwd=R);assert hashlib.sha256(oldraw).hexdigest()==p['beforeSourceSHA256']
b=json.loads(oldraw);raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw);before={o['id']:o for o in b['objects']};now={o['id']:o for o in s['objects']}
assert before.keys()==now.keys()
uv=set(r['roofUVMeshes']);maxerr=0;originals=0;newtri=0;newsolid=0
for n,o in before.items():
 q=now[n];assert {k:v for k,v in o.items() if k!='parts'}=={k:v for k,v in q.items() if k!='parts'},(n,'gameplay metadata')
 oldparts={a['id']:a for a in o['parts']};newparts={a['id']:a for a in q['parts']}
 assert newparts.keys()-oldparts.keys()==set(r['newParts'].get(n,[])) and not oldparts.keys()-newparts.keys(),n
 for name,a in oldparts.items():
  d=newparts[name];unlit=lambda v:{k:q for k,q in v.items() if k!='bakedLighting'}
  x,y=unlit(a),unlit(d)
  if name in uv:
   assert a['material'] in p['materialNames']
   olduv=x.pop('uvs');newuv=y.pop('uvs');assert len(olduv)==len(newuv)
   for f,g in zip(olduv,newuv):
    for v,w in zip(f,g):
     for t,u in zip(v,w):maxerr=max(maxerr,abs(t*p['roofUVFactor']-u))
  assert x==y,(n,name,'undeclared mesh change');originals+=1
 for name in r['newParts'].get(n,[]):
  a=newparts[name];newtri+=sum(len(f)-2 for f in a['faces']);newsolid+=a['role']=='solid'
assert maxerr<.000021 and newtri==r['addedVisibleTriangles']<p['triangleBudget']
assert newsolid==r['newSolidPosts']==38
assert s['terrain']==b['terrain'] and s['navigation']==b['navigation']
for key in b.keys()-{'objects','materials','lighting'}:assert s[key]==b[key],key
assert s['materials'].keys()==b['materials'].keys()
for n,m in b['materials'].items():assert s['materials'][n]==r['materialChanges'].get(n,{}).get('after',m),n
assert {k:v for k,v in b['lighting'].items() if k!='groundShadow'}=={k:v for k,v in s['lighting'].items() if k!='groundShadow'}
assert s['lighting']['groundShadow']['file']=='assets/wayfarer-ground-shadow-v78-frontages.png' and s['lighting']['groundShadow']['resolution']==4096
for n,sha in p['originalImages'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==sha,n
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2,cap_style=2,join_style=2) for a in layout['roads']])
feet=unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull for o in b['objects'] for a in o['parts'] if a['role']=='solid'])
patrols=unary_union([LineString(w['route']+[w['route'][0]]).buffer(.38) for o in s['objects'] for w in o.get('walkers',[]) if len(w['route'])>1])
placements=[]
for a in p['frontages']:
 lot=next(l for l in layout['lots'] if l['id']==a['id']);zone=Polygon(lot['lot']);o=now[a['id']]
 new=[q for q in o['parts'] if q['id'] in r['newParts'][a['id']]]
 roof=MultiPoint([v[:2] for q in new if q['role']=='overhead' for v in q['vertices']]).convex_hull
 assert roof.hausdorff_distance(Polygon(a['roofFootprint']))<.00003,(a['id'],'native roof does not match planned placement')
 assert zone.buffer(.03).covers(roof) and roof.intersection(roads).area<.00001,a['id']
 direction=[-math.sin(a['angle']),math.cos(a['angle'])];dc=a['position'][:2];approach=LineString([dc,[dc[i]+direction[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2)
 posts=[q for q in new if q['role']=='solid'];assert len(posts)==2
 for q,planned in zip(posts,a['postFootprints']):
  foot=MultiPoint([v[:2] for v in q['vertices']]).convex_hull
  assert any(foot.hausdorff_distance(Polygon(poly))<.00004 for poly in a['postFootprints'])
  assert not foot.intersects(approach) and not foot.intersects(roads) and not foot.buffer(.079).intersects(feet) and not foot.intersects(patrols),(a['id'],'post clearance')
  assert abs(min(v[2] for v in q['vertices'])-.04)<.000021,(a['id'],'post not on actual paving')
 for q in new:
  assert zone.buffer(.05).covers(MultiPoint([v[:2] for v in q['vertices']])),(a['id'],q['id'],'component outside own plot')
  if q['role']=='overhead':assert min(v[2] for v in q['vertices'])>a['doorTop']+.15
 placements.append({'id':a['id'],'style':a['style'],'ownedPlot':True,'entranceClearWidth':2.2,'streetAndClosedRoutesClear':True})
assert len({a['style'] for a in placements})==4
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'baselineSourceSHA256':p['beforeSourceSHA256'],'originalPartsExactExceptDeclaredRoofUVsAndRebakedLight':originals,'roofUVMaximumError':maxerr,'newVisibleTriangles':newtri,'newSolidPosts':newsolid,'placements':placements,'originalImageBytesAndResolutionExact':True,'additionalImageAssets':0,'terrainNavigationGameplayExact':True,'pass':True,'visualAcceptance':'Separate human gameplay comparison required'}
(O/'declared-delta.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='placements'},indent=2))
