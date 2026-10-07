"""Independently check rendered planting, actual doors and retained source data."""
import json,hashlib,runpy
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76'
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
plan=json.loads((O/'beta-edge-plan.json').read_text());p=json.loads((O/'native-plan.json').read_text())
assert runpy.run_path(str(R/'tools/capital-beta-edge-integrity-v76.py'))['preserved_digest'](s)==plan['preservedSourceDigest'],'An unapproved source field changed'
assert s['materials']['publicTownStone']['texture']['worldSize']==3.2
assert s['materials']['houseApronPaving']['texture']['worldSize']==8
assert s['lighting'].get('groundShadow'),'Source-matched ground shadows must remain installed'
objects={o['id']:o for o in s['objects']};cover=objects['capital-beta-frontage-groundcover'];assert cover['family']=='vegetation'
expected={a['id']:a for a in plan['pieces']};assert {a['id'] for a in cover['parts']}==set(expected)
triangles=[];max_vertex_error=0
for a in cover['parts']:
    assert a['role']=='decorative' and not a['shadow'] and a['material']=='grass'
    assert a['faces']==expected[a['id']]['faces']
    assert len(a['vertices'])==len(expected[a['id']]['vertices'])
    error=max(abs(x-y) for actual,wanted in zip(a['vertices'],expected[a['id']]['vertices']) for x,y in zip(actual,wanted))
    max_vertex_error=max(max_vertex_error,error)
    # Native coordinates are Float32, then exported at five decimals. At this
    # city's <256-unit coordinates this bound covers only representational error.
    assert error<.00002,('Native planting vertex moved',a['id'],error)
    assert all(abs(v[2]-.047)<1e-6 for v in a['vertices'])
    for f in a['faces']:
        vs=[a['vertices'][i] for i in f];q=Polygon([v[:2] for v in vs])
        assert q.area>1e-10 and q.exterior.is_ccw,'Groundcover face must point upward'
        triangles.append(q)
green=unary_union(triangles);assert abs(sum(t.area for t in triangles)-green.area)<.001,'Overlapping planting triangles'
private=unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<1e-4 for v in a['vertices']) for f in a['faces']])
assert green.difference(private.buffer(.00002)).area<.001,'Planting escaped its actual flat private paving'
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.1,cap_style=2,join_style=2) for a in p['roads']])
assert green.intersection(roads).area<.001,'Planting interrupts a public road'
solid=[];entries=[]
for o in s['objects']:
    for a in o['parts']:
        if a['role']=='solid' and min(v[2] for v in a['vertices'])<1:solid.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.15))
for l in p['lots']:
    for a in objects[l['id']]['parts']:
        if 'door' not in a['id'] or 'leaf' not in a['id']:continue
        vs=a['vertices'];extent=[max(v[i] for v in vs)-min(v[i] for v in vs) for i in (0,1)]
        axis=0 if extent[0]<extent[1] else 1;center=[sum(v[i] for v in vs)/len(vs) for i in (0,1)]
        normal=[0,0];normal[axis]=1 if center[axis]>l['center'][axis] else -1
        entries.append(LineString([center,[center[i]+normal[i]*3.8 for i in (0,1)]]).buffer(.95,cap_style=2))
assert green.intersection(unary_union(solid)).area<.001,'Planting intersects physical feet'
assert green.intersection(unary_union(entries)).area<.001,'Planting crosses an actual entrance path'
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'beforeSourceSHA256':plan['beforeSourceSHA256'],'preservedSourceDigest':plan['preservedSourceDigest'],'publicStoneWorldSize':3.2,'privateStoneWorldSize':8,'plantingPieces':len(cover['parts']),'plantingTriangles':len(triangles),'plantedArea':green.area,'actualDoorPathsChecked':len(entries),'publicRoadOverlapArea':green.intersection(roads).area,'privateOwnershipVerified':True,'allOtherSourceFieldsPreserved':True,'existingShadowBakeRetained':True,'additionalTextures':0,'additionalCollisionObstacles':0,'pass':True}
report['maximumPlannedVertexError']=max_vertex_error
(O/'beta-edge-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
