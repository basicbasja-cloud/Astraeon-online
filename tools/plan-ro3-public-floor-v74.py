"""Separate public stone from owned lot paving and remove coplanar plaza overlap.

Plan from saved indexed faces, preserving floor heights and all stairs. Requires
Shapely 2.1.2; the companion authors these changes into the saved Blender town.
"""
import argparse
import json
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
w = json.loads((ROOT / 'world/v3/wayfarer-spatial.json').read_text())
native = json.loads((ROOT / 'docs/review/wayfarer-v72/native.json').read_text())
private = unary_union([Polygon(a['outer'], a['holes']) for z in native['zones'] for a in z['outline']])

def footprint(s):
    return unary_union([Polygon([s['vertices'][i][:2] for i in f]) for f in s['faces']]).buffer(0)

def triangles(p):
    return [list(t.exterior.coords)[:3] for t in constrained_delaunay_triangles(p).geoms if t.area > 1e-10]

surfaces = w['terrain']['surfaces']
court = unary_union([footprint(s) for s in surfaces if s['id'] == 'organic-v47-civic-court' or s['id'].startswith('blueprint72-cross-')])
records = []
for s in surfaces:
    if not s['visible'] or not s['walkable'] or s['material'] not in {'paving', 'cityPaving', 'houseApronPaving', 'avenuePaving', 'publicSquareStone'}:
        continue
    if any(k in s['id'] for k in ('tread', 'step', 'stair')):
        continue
    zs = [v[2] for v in s['vertices']]
    if max(zs) - min(zs) > .0001:
        continue
    original = footprint(s)
    p = original
    if s['id'] == 'city-v48-continuous-stone-interior':
        p = p.difference(court)
    if s['material'] in {'avenuePaving', 'publicSquareStone'}:
        records.append({'id': s['id'], 'z': zs[0], 'regions': [{'material': s['material'], 'retainMesh': True}], 'removedArea': 0})
        continue
    regions = []
    for material, region in [('publicTownStone', p.difference(private)), ('houseApronPaving', p.intersection(private))]:
        if region.area > 1e-8:
            regions.append({'material': material, 'triangles': triangles(region), 'area': region.area})
    assert regions, s['id']
    error = abs(sum(r['area'] for r in regions) - p.area)
    assert error < .00001, (s['id'], error)
    records.append({'id': s['id'], 'z': zs[0], 'regions': regions, 'beforeArea': original.area, 'removedArea': original.area - p.area})

plan = {'version': 74, 'rule': 'Continuous world-space public stone; rectangular paving within closed private zones and on stairs.', 'surfaces': records}
args.output.write_text(json.dumps(plan, indent=2) + '\n')
print('Planned', len(records), 'flat floors;', round(sum(r['removedArea'] for r in records), 3), 'm² of duplicate plaza/approach backing removed')
