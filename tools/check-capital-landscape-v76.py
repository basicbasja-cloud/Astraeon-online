"""Independent rendered lawn ownership, entry clearance and crown checks."""
import json, hashlib, math
from pathlib import Path
from shapely.geometry import Polygon, MultiPoint, LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
p=json.loads((O.parent/'native-plan.json').read_text());plan=json.loads((O/'natural-lawns-plan.json').read_text());author=json.loads((O/'landscape-authoring.json').read_text())
objects={o['id']:o for o in s['objects']}
cover=objects['capital-beta-frontage-groundcover'];assert len(cover['parts'])==len(plan['pieces'])
def region(parts):return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
actual={a['id']:a for a in cover['parts']}
for expected in plan['pieces']:
    part=actual[expected['id']]
    assert part['role']=='decorative' and not part['shadow'] and part['material']=='grass'
    assert part['faces']==expected['faces']
    assert len(part['vertices'])==len(expected['vertices'])
    assert max(abs(x-y) for a,b in zip(part['vertices'],expected['vertices']) for x,y in zip(a,b))<.00002
    if plan.get('nativeEdgeOpacity'):
        assert len(part['vertexOpacity'])==len(part['vertices'])
        assert part['vertexOpacity']==expected['vertexOpacity']
        assert min(part['vertexOpacity'])<.001 and max(part['vertexOpacity'])>.99
        assert .03<=expected['featherWidth']<=.28
    for face,uv in zip(part['faces'],part['uvs']):
        for i,q in zip(face,uv):assert max(abs(q[j]-part['vertices'][i][j]/7) for j in (0,1))<.00002
green=region(cover['parts'])
tri_area=sum(Polygon([a['vertices'][i][:2] for i in f]).area for a in cover['parts'] for f in a['faces'])
assert abs(tri_area-green.area)<.001,'Overlapping lawn triangles'
if plan.get('nativeEdgeOpacity'):
    prior=json.loads((O/'natural-lawns-before-feather.json').read_text())
    prior_mask=region(prior['pieces']);planned_mask=region(plan['pieces'])
    assert planned_mask.symmetric_difference(prior_mask).area<.000001,'Feather changed the planned ownership mask'
    # Blender stores Float32 points and the export rounds to five decimals.
    # Bound mask drift by its perimeter and the independently checked point
    # precision, rather than an arbitrary whole-city area threshold.
    mask_error=green.symmetric_difference(prior_mask).area
    mask_budget=prior_mask.length*math.sqrt(2)*.00002+.001
    assert mask_error<mask_budget,'Native planted boundary exceeds coordinate precision'
    assert plan['edgeBlending']['addedTriangles']<plan['edgeBlending']['triangleBudget']==20000
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<1e-4 for v in a['vertices'])])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.12,cap_style=2,join_style=2) for a in p['roads']])
assert green.difference(private.buffer(.00002)).area<.001
assert green.intersection(roads).area<.001
entries=[]; feet=[]
for lot in p['lots']:
    heading=lot['angle']+lot.get('frontageOffset',0);normal=(-math.sin(heading),math.cos(heading))
    for a in objects[lot['id']]['parts']:
        if not a['id'].endswith('-door-leaf'):continue
        center=[sum(v[i] for v in a['vertices'])/len(a['vertices']) for i in (0,1)]
        entries.append(LineString([center,[center[i]+normal[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
for o in s['objects']:
    for a in o['parts']:
        if a['role']=='solid' and min(v[2] for v in a['vertices'])<1:feet.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.20))
assert green.intersection(unary_union(entries)).area<.001
assert green.intersection(unary_union(feet)).area<.001
corners=0
for tree in author['trees']:
    parts={a['id']:a for a in objects[tree['id']]['parts']}
    assert sum(len(f)-2 for n in tree['parts'] for f in parts[n]['faces'])==720
    for n in tree['parts']:
        a=parts[n];assert a['shadow'] and a['role']=='overhead' and a.get('bakedLighting')
        for face in a['faces']:
            x,y,z=[a['vertices'][i] for i in face[:3]]
            assert (y[0]-x[0])*(z[1]-x[1])-(y[1]-x[1])*(z[0]-x[0])>0,(n,'downward bough')
        assert max(abs(q) for f in a['uvs'] for uv in f for q in uv)<=1.00001
        assert all(len(f)==len(light) for f,light in zip(a['faces'],a['bakedLighting']))
        corners+=sum(len(f) for f in a['faces'])
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'plantedArea':green.area,'previousPlantedArea':plan['oldArea'],
        'pieces':len(cover['parts']),'triangles':sum(len(a['faces']) for a in cover['parts']),
        'privateOwnershipVerified':True,'roadsClear':True,'actualEntrancePaths':len(entries),'entranceClearWidth':2.2,
        'allPhysicalFeetClear':True,'trees':len(author['trees']),'boughsPerTree':90,'originalAlphaBakedCorners':corners,
        'additionalTextures':0,'additionalObstacles':0,'pass':True,'visualAcceptance':'Requires gameplay image review'}
if plan.get('nativeEdgeOpacity'):
    report['grassStoneTransition']={**plan['edgeBlending'],'plannedOwnershipMaskExactlyPreserved':True,
        'nativeMaskRoundingArea':mask_error,'nativeMaskRoundingBudget':mask_budget}
(O/'landscape-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
