"""One-shot native crown sculpt; keep all existing topology, Z, UVs and roots."""
import bpy
import gc
import hashlib
import json
import math
import runpy
from pathlib import Path
from mathutils import Vector

R = Path(__file__).resolve().parents[1]
O = R / 'docs/review/wayfarer-capital-v83/layered-crowns'
s = bpy.context.scene
assert not s.get('capital_layered_crowns_v83'), 'Already applied; do not rerun'
p = json.loads((O / 'plan.json').read_text())
base = json.loads((O / 'baseline.json').read_text())
assert hashlib.sha256((R / 'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest() == p['beforeSourceSHA256']
assert hashlib.sha256((R / 'authoring/wayfarer-spatial.blend').read_bytes()).hexdigest() == p['beforeNativeSHA256']
helper = runpy.run_path(str(R / 'tools/capital-neighborhood-proof-v80.py'))
fp, unlit, meta = helper['fingerprint'], helper['unlit'], helper['metadata']
changed = set()
records = []
for a in p['trees']:
    c = bpy.data.collections[a['id']]
    cx, cy = a['center']
    boughs = 0
    lower = 0
    for name in a['parts']:
        o = bpy.data.objects[name]
        assert o in c.objects[:] and o.get('conifer_v70') and len(o.data.vertices) % 9 == 0
        assert abs(o.matrix_world[2][0]) < 1e-8 and abs(o.matrix_world[2][1]) < 1e-8
        inv = o.matrix_world.inverted()
        for start in range(0, len(o.data.vertices), 9):
            points = [o.matrix_world @ o.data.vertices[start+j].co for j in range(9)]
            z = sum(v.z for v in points[:3]) / 3
            tier = round(((z-a['base'])/a['height']-.31)/.69*8)
            assert 0 <= tier <= 8, (name, tier)
            angle = math.atan2(points[4].y-cy, points[4].x-cx)
            oldrad = max(math.hypot(v.x-cx, v.y-cy) for v in points)
            irregular = .945 + .033*math.sin(angle*3+a['variationPhase']+tier*.6) + .018*math.cos(angle*5-tier*.37)
            desired = a['radiusBudget'] * a['profile'][tier] * irregular
            # Keep low branches inside their original envelope. Only the high
            # middle canopy broadens into measured clear space above paths.
            low = min(v.z-a['base'] for v in points) < a['lowCanopyClearHeight']
            if low:
                desired = min(desired, oldrad)
                lower += 1
            scale = desired/oldrad
            yaw = 0 if low else a['maximumBoughYawRadians']*math.sin(angle*2+a['variationPhase']+tier*.71)
            co, si = math.cos(yaw), math.sin(yaw)
            for j, q in enumerate(points):
                x, y = (q.x-cx)*scale, (q.y-cy)*scale
                q.x, q.y = cx+co*x-si*y, cy+si*x+co*y
                local = inv @ q
                o.data.vertices[start+j].co.x = local.x
                o.data.vertices[start+j].co.y = local.y
            boughs += 1
        old = o.data.color_attributes.get('BakedTownLight')
        if old:
            o.data.color_attributes.remove(old)
        o.data.update()
        assert all(f.normal.z > 0 for f in o.data.polygons), name
        o['layered_crown_v83'] = True
        changed.add(name)
    assert boughs == 90, (a['id'], boughs)
    records.append({'id': a['id'], 'boughs': boughs, 'lowBoughsNotExpanded': lower,
                    'height': a['height'], 'radiusBudget': a['radiusBudget'], 'profile': a['profile']})

exp = runpy.run_path(str(R / 'tools/export-world-v3.py'))
world = exp['export'](s)
specs = {a['id']: a for a in p['trees']}
assert set(o['id'] for o in world['objects']) == set(base['owners'])
for o in world['objects']:
    b = base['owners'][o['id']]
    assert fp(meta(o)) == b['metadata'], (o['id'], 'gameplay metadata')
    assert set(a['id'] for a in o['parts']) == set(b['parts'])
    for part in o['parts']:
        if part['id'] not in changed:
            assert fp(unlit(part)) == b['parts'][part['id']], (o['id'], part['id'])
        else:
            assert fp({**unlit(part), 'vertices': [[0, 0, v[2]] for v in part['vertices']]}) == specs[o['id']]['leafGeometryExceptXY'][part['id']], (part['id'], 'Z/topology/UV changed')
assert world['materials'] == base['materials']
assert fp({k: v for k, v in world.items() if k not in ('objects', 'materials', 'lighting')}) == base['common']
triangles = sum(len(f)-2 for o in world['objects'] for part in o['parts'] if part.get('visible', True) for f in part['faces'])
assert triangles == p['beforeVisibleTriangles']
city = json.loads(s['capital_plan_json'])
city['layeredCrownRefinement'] = {'revision': 83, 'trees': records, 'newTriangles': 0, 'newImages': 0}
s['capital_plan_json'] = json.dumps(city)
s['capital_layered_crowns_v83'] = 1
s['ground_shadow_asset'] = 'assets/wayfarer-ground-shadow-v83-layered-crowns.png'
for name in ('plan.json', 'native-plan.json'):
    (O.parent/name).write_text(json.dumps(city, indent=2)+'\n')
(O/'authoring.json').write_text(json.dumps({'beforeSourceSHA256': p['beforeSourceSHA256'],
    'trees': records, 'changedLeafParts': sorted(changed), 'newTriangles': 0, 'newImages': 0,
    'rootsTrunksTopologyUVsMaterialsAndOtherWorldPartsRetained': True,
    'visualAcceptance': 'Pending source-matched gameplay review'}, indent=2)+'\n')
del world, base
gc.collect()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'), compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'), run_name='__main__')
print('PASS saved', len(records), 'layered crowns; no added triangles or images', flush=True)
