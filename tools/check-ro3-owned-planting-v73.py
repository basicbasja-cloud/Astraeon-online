"""Verify actual exported plant placement and preservation, independently of bpy."""
import argparse
import json
import math
from pathlib import Path
from shapely.geometry import Polygon, Point, MultiPoint
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--plan', type=Path, required=True)
ap.add_argument('--before', type=Path, required=True)
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
before = json.loads(args.before.read_text())
after = json.loads((ROOT / 'world/v3/wayfarer-spatial.json').read_text())
plan = json.loads(args.plan.read_text())
zones = json.loads((ROOT / 'docs/review/wayfarer-v72/native.json').read_text())['zones']
private = unary_union([Polygon(a['outer'], a['holes']) for z in zones for a in z['outline']])
old_parts = {p['id']: p for o in before['objects'] for p in o['parts']}
new_parts = {p['id']: p for o in after['objects'] for p in o['parts']}
assert set(old_parts) == set(new_parts), 'No parts may be removed or substituted'
for field in ('navigation', 'spawn', 'safeSpawn', 'route', 'districts'):
    assert before.get(field) == after.get(field), field
assert [a for o in before['objects'] for a in o.get('walkers', [])] == [a for o in after['objects'] for a in o.get('walkers', [])]
assert [a for o in before['objects'] for a in o.get('services', [])] == [a for o in after['objects'] for a in o.get('services', [])]
changes = {}
for fit in plan['treeFits']:
    names = ([p['id'] for o in before['objects'] if o['id'] == 'plaza-oak-east' for p in o['parts']]
             if fit['id'] == 'plaza-oak-east-root' else
             [name for name in old_parts if 'garden-v4-tree-7-' in name])
    for name in names:
        changes[name] = lambda v, delta=fit['delta']: [v[i]+delta[i] for i in range(3)]
for fit in plan['clusters']:
    angle = fit['rotation']
    def transform(v, f=fit, c=math.cos(angle), s=math.sin(angle)):
        x, y = v[0]-f['before'][0], v[1]-f['before'][1]
        return [f['after'][0]+c*x-s*y, f['after'][1]+s*x+c*y, v[2]-f['oldFloor']+f['floor']]
    for name in fit['parts']:
        assert name not in changes, ('duplicate plant ownership', name)
        changes[name] = transform
maximum_error = 0
for name, old in old_parts.items():
    new = new_parts[name]
    for field in ('faces', 'uvs', 'material', 'role', 'shadow', 'visible', 'bakedLighting'):
        assert old.get(field) == new.get(field), (name, field)
    if name not in changes:
        assert old['vertices'] == new['vertices'], ('unplanned geometry edit', name)
        continue
    assert len(old['vertices']) == len(new['vertices'])
    for a, b in zip(old['vertices'], new['vertices']):
        error = math.dist(changes[name](a), b)
        maximum_error = max(maximum_error, error)
        assert error < .00006, (name, error)
covered = []
for fit in plan['clusters']:
    for group in fit['groups']:
        soil = new_parts[f'flora-v64-{group}-soil']
        footprint = MultiPoint([v[:2] for v in soil['vertices']]).convex_hull
        assert private.buffer(.00002).covers(footprint), ('plant outside private zone', group)
        covered.append(group)
contacts = json.loads((ROOT / 'docs/review/wayfarer-v72/resumed/tree-contacts-after.json').read_text())
for fit in plan['treeFits']:
    assert abs(contacts[fit['id']]['offset']+.015) < .00003, contacts[fit['id']]
report = {'status': 'passed', 'flowerGroupsInPrivateMargins': len(covered),
          'wholeClusters': len(plan['clusters']), 'repairedTreeContacts': {f['id']: contacts[f['id']] for f in plan['treeFits']},
          'partsTransformed': len(changes), 'maxTransformError': maximum_error,
          'geometryArtworkAndUVPreserved': True, 'actorNavigationAndServiceDataPreserved': True}
args.output.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report), flush=True)
