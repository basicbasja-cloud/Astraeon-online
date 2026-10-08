"""Verify the measured crown delta independently from the native sculpt."""
import argparse
import hashlib
import json
import math
import runpy
from pathlib import Path
from shapely.geometry import MultiPoint
from shapely.ops import unary_union

R = Path(__file__).resolve().parents[1]
O = R / 'docs/review/wayfarer-capital-v83/layered-crowns'
ap = argparse.ArgumentParser()
ap.add_argument('--pending-light', action='store_true')
args = ap.parse_args()
p = json.loads((O/'plan.json').read_text())
base = json.loads((O/'baseline.json').read_text())
receipt = json.loads((O/'authoring.json').read_text())
helper = runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'))
fp, unlit, meta = helper['fingerprint'], helper['unlit'], helper['metadata']
raw = (R/'world/v3/wayfarer-spatial.json').read_bytes()
sha = hashlib.sha256(raw).hexdigest()
s = json.loads(raw)
del raw
now = {o['id']: o for o in s['objects']}
chosen = {a['id']: a for a in p['trees']}
changed = {n for a in p['trees'] for n in a['parts']}
assert changed == set(receipt['changedLeafParts'])
assert set(now) == set(base['owners'])
retained = 0
for n, o in now.items():
    b = base['owners'][n]
    assert fp(meta(o)) == b['metadata'], (n, 'metadata changed')
    assert set(a['id'] for a in o['parts']) == set(b['parts']), n
    for a in o['parts']:
        if a['id'] not in changed:
            assert fp(unlit(a)) == b['parts'][a['id']], (n, a['id'], 'undeclared edit')
            retained += 1
        else:
            assert n in chosen and a['material'].startswith('conifer70') and a['role'] == 'overhead' and a['shadow']
            digest = fp({**unlit(a), 'vertices': [[0, 0, v[2]] for v in a['vertices']]})
            assert digest == chosen[n]['leafGeometryExceptXY'][a['id']], (n, a['id'], 'Z/face/UV/material changed')
            assert fp(unlit(a)) != b['parts'][a['id']], (n, 'crown was not changed')
            if not args.pending_light:
                assert a.get('bakedLighting') and all(len(f)==len(light) for f,light in zip(a['faces'],a['bakedLighting']))
assert fp({k:v for k,v in s.items() if k not in ('objects','materials','lighting')}) == base['common']
assert s['materials'] == base['materials']
assert {k:v for k,v in s['lighting'].items() if k!='groundShadow'} == {k:v for k,v in base['lighting'].items() if k!='groundShadow'}
if not args.pending_light:
    assert s['lighting']['groundShadow']['file'] == 'assets/wayfarer-ground-shadow-v83-layered-crowns.png'
    assert s['lighting']['groundShadow']['resolution'] == 4096
for f, digest in base['images'].items():
    assert hashlib.sha256((R/f).read_bytes()).hexdigest() == digest, f

roofs = unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull
                    for o in s['objects'] if o['family']!='vegetation'
                    for a in o['parts'] if a.get('visible',True) and a['role']=='overhead'])
crown_polygons = {}
for n,o in now.items():
    vs = [v[:2] for a in o['parts'] if a.get('visible',True) and a['material'].startswith('conifer70') for v in a['vertices']]
    if vs:
        crown_polygons[n] = MultiPoint(vs).convex_hull
proof = []
for n,a in chosen.items():
    parts = [q for q in now[n]['parts'] if q['id'] in a['parts']]
    vs = [v for q in parts for v in q['vertices']]
    assert sum(len(f)-2 for q in parts for f in q['faces']) == 720
    assert max(math.dist(v[:2],a['center']) for v in vs) < a['radiusBudget']+.00003
    assert abs(max(v[2] for v in vs)-a['base']-a['height']) < .00003
    crown = crown_polygons[n]
    assert crown.distance(roofs) >= a['roofClearance']-.00004, (n,'roof contact')
    for other,poly in crown_polygons.items():
        if other != n:
            assert not crown.intersects(poly), (n,other,'crowns collide')
    for q in parts:
        for start,old_radius in a['lowerBoughRadii'][q['id']]:
            assert max(math.dist(v[:2],a['center']) for v in q['vertices'][start:start+9]) <= old_radius+.00004, (n,'low canopy expanded into walking space')
        for f in q['faces']:
            x,y,z = [q['vertices'][i] for i in f[:3]]
            assert (y[0]-x[0])*(z[1]-x[1])-(y[1]-x[1])*(z[0]-x[0]) > 0, (n,'downward bough')
    proof.append({'id':n,'height':a['height'],'actualRadius':max(math.dist(v[:2],a['center']) for v in vs),
                  'roofClearance':crown.distance(roofs),'rootsAndUVsExact':True,'triangles':720})
tri = sum(len(f)-2 for o in s['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces'])
assert tri == p['beforeVisibleTriangles']
report = {'sourceSHA256':sha,'pass':True,'lightingVerified':not args.pending_light,
          'retainedOriginalParts':retained,'changedLeafParts':len(changed),'selectedCrowns':proof,
          'allOwnersRootsTrunksCollisionTerrainNavigationGameplayExact':True,
          'allLeafZTopologyUVsMaterialsExact':True,'existingImageBytesAndResolutionExact':True,
          'newTriangles':0,'newImages':0,'newMaterials':0,
          'visualAcceptance':'Requires source-matched ordinary gameplay review'}
(O/('geometry-candidate.json' if args.pending_light else 'declared-delta.json')).write_text(json.dumps(report,indent=2)+'\n')
print('PASS',len(chosen),'measured crowns;',retained,'other parts retained; no added triangles/images')
