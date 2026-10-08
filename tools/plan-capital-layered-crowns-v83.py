"""Measure a bounded crown pass from the sealed v82 scene; do not mutate it."""
import hashlib
import json
import math
import runpy
from pathlib import Path

from shapely.geometry import MultiPoint, Point
from shapely.ops import unary_union

R = Path(__file__).resolve().parents[1]
O = R / 'docs/review/wayfarer-capital-v83/layered-crowns'
seal = json.loads((R / 'docs/review/wayfarer-capital-v82/grounded-frontages/verified-source.json').read_text())
raw = (R / 'world/v3/wayfarer-spatial.json').read_bytes()
sha = hashlib.sha256(raw).hexdigest()
assert seal['pass'] and sha == seal['sourceSHA256']
assert hashlib.sha256((R / 'authoring/wayfarer-spatial.blend').read_bytes()).hexdigest() == seal['nativeSHA256']
s = json.loads(raw)
del raw
O.mkdir(parents=True, exist_ok=True)
helper = runpy.run_path(str(R / 'tools/capital-neighborhood-proof-v80.py'))
fp, unlit, meta = helper['fingerprint'], helper['unlit'], helper['metadata']
baseline = {'sourceSHA256': sha, 'nativeSHA256': seal['nativeSHA256'], 'owners': {},
            'materials': s['materials'], 'lighting': s['lighting'],
            'common': fp({k: v for k, v in s.items() if k not in ('objects', 'materials', 'lighting')})}
for o in s['objects']:
    baseline['owners'][o['id']] = {'metadata': fp(meta(o)), 'parts': {a['id']: fp(unlit(a)) for a in o['parts']}}
images = {m['texture']['file'] for m in s['materials'].values() if m.get('texture')}
baseline['images'] = {f: hashlib.sha256((R / f).read_bytes()).hexdigest() for f in images}
(O / 'baseline.json').write_text(json.dumps(baseline, separators=(',', ':')) + '\n')

roofs = unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull
                    for o in s['objects'] if o['family'] != 'vegetation'
                    for a in o['parts'] if a.get('visible', True) and a['role'] == 'overhead'])
trees = {}
for o in s['objects']:
    if o['family'] != 'vegetation':
        continue
    stem = [v for a in o['parts'] if a['role'] == 'solid' for v in a['vertices']]
    leaves = [a for a in o['parts'] if a.get('visible', True) and a['material'].startswith('conifer70')]
    if not stem or not leaves:
        continue
    center = [(min(v[i] for v in stem) + max(v[i] for v in stem)) / 2 for i in (0, 1)]
    base = min(v[2] for v in stem)
    vs = [v for a in leaves for v in a['vertices']]
    trees[o['id']] = {'id': o['id'], 'center': center, 'base': base,
                     'height': max(v[2] for v in vs) - base,
                     'beforeRadius': max(math.dist(v[:2], center) for v in vs),
                     'parts': [a['id'] for a in leaves],
                     'lowerBoughRadii': {a['id']: [[i, max(math.dist(v[:2], center) for v in a['vertices'][i:i+9])]
                                                  for i in range(0, len(a['vertices']), 9)
                                                  if min(v[2]-base for v in a['vertices'][i:i+9]) < 2.4] for a in leaves},
                     'leafGeometryExceptXY': {a['id']: fp({**unlit(a), 'vertices': [[0, 0, v[2]] for v in a['vertices']]}) for a in leaves}}

chosen = {n for n in trees if n.startswith('capital-street-tree-v77-') or n.startswith('plaza-oak-')}
chosen.update(f'capital-tree-{i:03}' for i in (26, 27, 28, 29, 32, 33, 34, 35, 64, 66, 68, 69, 70, 71, 73, 75))
assert chosen <= set(trees)
profiles = [[.82, .98, .96, .87, .74, .58, .41, .25, .06],
            [.86, .99, .94, .82, .71, .59, .44, .27, .06],
            [.79, .95, .99, .90, .76, .61, .42, .26, .06]]
selections = []
rejected = []
for n in sorted(chosen):
    a = trees[n]
    roof_distance = roofs.distance(Point(a['center']))
    neighbor_budget = min(math.dist(a['center'], b['center']) / 2 - .15 if b['id'] in chosen
                          else math.dist(a['center'], b['center']) - b['beforeRadius'] - .15
                          for b in trees.values() if b['id'] != n)
    budget = min(a['beforeRadius'] * 1.32, roof_distance - .20, neighbor_budget)
    if budget < a['beforeRadius'] * 1.04:
        rejected.append({'id': n, 'radiusBudget': budget, 'beforeRadius': a['beforeRadius'], 'reason': 'Insufficient safe broadening clearance'})
        continue
    seed = int(hashlib.sha256(n.encode()).hexdigest()[:8], 16)
    selections.append({**a, 'radiusBudget': budget, 'roofClearance': .20, 'roofDistance': roof_distance,
                       'profile': profiles[seed % len(profiles)], 'variationPhase': (seed % 1000) / 1000 * math.tau,
                       'lowCanopyClearHeight': 2.4, 'maximumBoughYawRadians': .045})
assert len(selections) >= 16, (len(selections), rejected)
plan = {'baselineCommit': '2932d577662e041ce808c959c435f5efaa3ef6ab',
        'beforeSourceSHA256': sha, 'beforeNativeSHA256': seal['nativeSHA256'],
        'trees': selections, 'rejected': rejected, 'maximumRadiusFactor': 1.32,
        'beforeVisibleTriangles': sum(len(f)-2 for o in s['objects'] for a in o['parts'] if a.get('visible', True) for f in a['faces']),
        'references': ['Gates_Walls_Bridge_04m25s.jpg', 'Houses_Shops_Roofs_01m40s.jpg'],
        'policy': 'Broader layered middle crowns with bounded uneven branch tips. Preserve every trunk, root, collision, leaf Z coordinate, face, UV corner, material, image, tree position and other world part. Do not expand any bough with leaves below 2.4m. Measured roof and neighboring crown envelopes stay clear.'}
(O / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
print(json.dumps({'selectedTrees': len(selections), 'rejected': rejected,
                  'radii': [[a['id'], round(a['beforeRadius'], 3), round(a['radiusBudget'], 3)] for a in selections],
                  'newTriangles': 0, 'newImages': 0}, indent=2))
