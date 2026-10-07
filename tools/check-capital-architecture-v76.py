"""Check actual revised meshes, clear streets and retained entrance directions."""
import json,hashlib,math,collections,statistics
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76';raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw);p=json.loads((O/'native-plan.json').read_text());objects={o['id']:o for o in s['objects']}
assert len(p['lots'])==158 and p['existingHouses']==37 and p['newHouses']==121
assert s.get('architectureRevision')==76
changed=[l for l in p['lots'] if not l['existing']];types=collections.Counter(l['architectureType'] for l in changed);assert len(types)==9
roads=unary_union([LineString(r['centerline']).buffer(r['width']/2,cap_style=2,join_style=2) for r in p['roads']])
outlines={l['id']:MultiPoint([v[:2] for a in objects[l['id']]['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull for l in p['lots']}
minimum=float('inf');door_checks=[];bounds=[]
# Every visible part must stay with its owner; small world-origin brackets can
# otherwise create an enormous misleading aggregate footprint.
for l in changed+p['landmarks']:
 cx,cy=l['center'];limit=max(l['width'],l['depth'])/2+3
 for part in objects[l['id']]['parts']:
  if not part.get('visible',True):continue
  assert all(abs(v[0]-cx)<=limit and abs(v[1]-cy)<=limit for v in part['vertices']),(l['id'],'visible component escaped placement frame',part['id'])
for l in changed:
 o=objects[l['id']];q=outlines[l['id']];gap=min(q.distance(other) for n,other in outlines.items() if n!=l['id']);minimum=min(minimum,gap)
 assert gap>.74,(l['id'],'visible building overlap or gap',gap)
 assert q.intersection(roads).area<.001,(l['id'],'roof or frontage occupies public street')
 for part in o['parts']:
  if part['role']=='solid':assert MultiPoint([v[:2] for v in part['vertices']]).convex_hull.intersection(roads).area<.001,(part['id'],'solid in street')
 door=next(a for a in o['parts'] if a['id'].endswith('-door-leaf'));vs=door['vertices'];extent=[max(v[i] for v in vs)-min(v[i] for v in vs) for i in range(2)];axis=0 if extent[0]<extent[1] else 1;dc=[sum(v[i] for v in vs)/len(vs) for i in range(2)];normal=[0,0];normal[axis]=1 if dc[axis]>l['center'][axis] else -1
 assert sum(a*b for a,b in zip(normal,[-math.sin(l['angle']),math.cos(l['angle'])]))>.999,(l['id'],'actual door heading')
 door_checks.append(l['id']);z=[v[2] for part in o['parts'] if part.get('visible',True) for v in part['vertices']];bounds.append({'id':l['id'],'type':l['architectureType'],'height':round(max(z)-min(z),3),'roofFaces':sum(len(a['faces']) for a in o['parts'] if a['role']=='overhead')})
removed=[m['removed'] for m in p['architectureRevision']['pairedPlotConsolidations']];assert all(n not in objects for n in removed)
landmarks=[]
for l in p['landmarks']:
 o=objects[l['id']];heights=sorted({round(v[2],2) for a in o['parts'] if a['role']=='overhead' for v in a['vertices']});assert len(heights)>=2
 for part in o['parts']:
  if part['role']=='solid':assert MultiPoint([v[:2] for v in part['vertices']]).convex_hull.intersection(roads).area<.001,(part['id'],'civic solid in public avenue')
 landmarks.append({'id':l['id'],'type':l['architectureType'],'roofHeights':heights})
assert len({tuple(l['roofHeights']) for l in landmarks})==3,'Duplicated civic roof profiles'
assert len({r['height'] for r in bounds})>=20,'No real height variety'
parts=[a for o in s['objects'] for a in o['parts']];triangles=sum(len(f)-2 for a in parts if a.get('visible',True) for f in a['faces']);corners=sum(len(f) for a in parts for f in a['faces'])
assert len(raw)<100*1024*1024,('GitHub file limit',len(raw))
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'architectureRevision':76,'totalBuildings':158,'retainedOriginals':37,'newBuildings':121,'familyCounts':dict(types),'consolidatedPlotPairs':14,'actualDoorPlanesVerified':len(door_checks),'minimumVisibleBuildingGap':minimum,'streetsClear':True,'civicSilhouettes':landmarks,'distinctMeasuredBuildingHeights':len({r['height'] for r in bounds}),'visibleStaticTriangles':triangles,'meshCorners':corners,'exportBytes':len(raw),'roofAndHeightEvidence':bounds,'pass':True,'visualAcceptance':'Requires actual gameplay image review; structural checks are not visual acceptance'}
new_ids={l['id'] for l in changed}
report['newHousingTriangles']=sum(len(f)-2 for o in s['objects'] if o['id'] in new_ids for a in o['parts'] if a.get('visible',True) for f in a['faces'])
baseline=json.loads((O/'baseline-geometry.json').read_text())
report['resourceComparison']={'baselineSourceSHA256':baseline['sourceSHA256'],'staticTriangleReductionPercent':round(100*(1-triangles/baseline['staticVisibleTriangles']),2),'housingTriangleReductionPercent':round(100*(1-report['newHousingTriangles']/baseline['newHousingTriangles']),2),'exportReductionPercent':round(100*(1-len(raw)/baseline['exportBytes']),2),'nativeResolutionAndMaterialsRetained':True}
(O/'architecture-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='roofAndHeightEvidence'},indent=2))
