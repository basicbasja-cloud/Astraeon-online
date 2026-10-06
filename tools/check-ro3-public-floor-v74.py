"""Independently verify paving ownership, coverage, UV continuity and preservation."""
import argparse
import json
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--before', type=Path, required=True)
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
before = json.loads(args.before.read_text())
after = json.loads((ROOT / 'world/v3/wayfarer-spatial.json').read_text())
plan = json.loads((ROOT / 'docs/review/wayfarer-v74/floor-plan.json').read_text())
native = json.loads((ROOT / 'docs/review/wayfarer-v72/native.json').read_text())
private = unary_union([Polygon(a['outer'], a['holes']) for z in native['zones'] for a in z['outline']])
old = {s['id']: s for s in before['terrain']['surfaces']}
new = {s['id']: s for s in after['terrain']['surfaces']}

def footprint(s):
    return unary_union([Polygon([s['vertices'][i][:2] for i in f]) for f in s['faces']]).buffer(0)

court = unary_union([footprint(s) for s in old.values() if s['id'] == 'organic-v47-civic-court' or s['id'].startswith('blueprint72-cross-')])
changed = set()
max_error = 0
uv_corners = 0
for fit in plan['surfaces']:
    name = fit['id']
    regions = [new[name]] + ([new[name + '-private74']] if len(fit['regions']) > 1 else [])
    changed.update(s['id'] for s in regions)
    target = footprint(old[name])
    if name == 'city-v48-continuous-stone-interior': target = target.difference(court)
    actual = unary_union([footprint(s) for s in regions])
    error = target.symmetric_difference(actual).area
    max_error = max(max_error, error)
    assert error < .003, (name, 'floor coverage changed', error)
    for s, specification in zip(regions, fit['regions']):
        assert s['material'] == specification['material']
        assert all(abs(v[2] - fit['z']) < .00001 for v in s['vertices']), (name, 'floor height changed')
        if s['material'] == 'houseApronPaving':
            assert footprint(s).difference(private).area < .001, (name, 'private paving outside boundary')
        if s['material'] == 'publicTownStone':
            assert footprint(s).intersection(private).area < .001, (name, 'public paving inside private lot')
        for face, uvs in zip(s['faces'], s['uvs']):
            for i, uv in zip(face, uvs):
                assert max(abs(uv[k] - s['vertices'][i][k] / 8) for k in (0, 1)) < .00001, (name, 'UV seam')
                uv_corners += 1
for name, surface in old.items():
    if name not in changed: assert new[name] == surface, (name, 'unplanned floor edit')
assert after['objects'] == before['objects'], 'Architecture, plants, actors or services changed'
for key in before:
    if key not in ('terrain', 'materials', 'lighting'): assert after[key] == before[key], key
for key in before['terrain']:
    if key != 'surfaces': assert after['terrain'][key] == before['terrain'][key], key
backing = unary_union([footprint(new[name]) for name in new if name == 'city-v48-continuous-stone-interior' or name == 'city-v48-continuous-stone-interior-private74'])
overlap = backing.intersection(court).area
assert overlap < .001, ('coplanar plaza backing remains', overlap)
report = {'status': 'passed', 'flatFloorsChecked': len(plan['surfaces']), 'worldUVCornersChecked': uv_corners,
          'maximumCoverageErrorM2': max_error, 'coplanarPlazaBackingAreaM2': overlap,
          'removedDuplicateBackingM2': sum(s['removedArea'] for s in plan['surfaces']),
          'stairsAndUnplannedFloorsPreserved': True, 'architecturePlantsActorsServicesPreserved': True}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
