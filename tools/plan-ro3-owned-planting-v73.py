"""Plan bounded flower/tree repairs from saved native geometry (Shapely 2.1.2).

Preserve each existing flower cluster's artwork and spacing. Fit complete
clusters into private, house-owned curb margins, outside solids and entrances.
Two inherited trees move off stair treads onto flat planted parcel margins.
Writes a plan only; the Blender companion applies it to the native source.
"""
import argparse
import json
import math
import re
from pathlib import Path
from shapely.geometry import Polygon, Point, MultiPoint
from shapely.ops import unary_union
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
w = json.loads((ROOT / 'world/v3/wayfarer-spatial.json').read_text())
record = json.loads((ROOT / 'docs/review/wayfarer-v72/native.json').read_text())
private = unary_union([Polygon(a['outer'], a['holes'])
                      for z in record['zones'] for a in z['outline']])
parts = {p['id']: p for o in w['objects'] for p in o['parts']}
solid_parts = [p for o in w['objects'] for p in o['parts'] if p['role'] == 'solid']
solids = [MultiPoint([v[:2] for v in p['vertices']]).convex_hull for p in solid_parts]
solid_index = STRtree(solids)
bodies = []
for owner in w['objects']:
    core = next((p for p in owner['parts'] if p['id'].endswith('-ground-core') or
                 p['id'].startswith('side-v59-') and p['id'].endswith('-lower-walls')), None)
    if core:
        bodies.append((owner['id'], MultiPoint([v[:2] for v in core['vertices']]).convex_hull))
entries = [Point(a['position'][:2]).buffer(.95) for o in w['objects'] for a in o.get('services', [])]
entries += [Point(a['approach'][:2]).buffer(.95) for o in w['objects'] for a in o.get('portals', [])]
entry_area = unary_union(entries)
floor_polys, floor_triangles, public_parts = [], [], []
for surface in w['terrain']['surfaces']:
    if not surface['visible'] or not surface['walkable']:
        continue
    public = (surface.get('centerline') and surface.get('width', 0) >= 1.8 or
              surface['material'] == 'publicSquareStone' or 'tread-' in surface['id'])
    for face in surface['faces']:
        for i in range(1, len(face)-1):
            tri = [surface['vertices'][j] for j in (face[0], face[i], face[i+1])]
            poly = Polygon([v[:2] for v in tri])
            if poly.area < 1e-10:
                continue
            floor_polys.append(poly)
            floor_triangles.append(tri)
            if public:
                public_parts.append(poly)
floor_index = STRtree(floor_polys)
public_area = unary_union(public_parts)

def floor(x, y):
    height = w['terrain']['elevation']
    for i in floor_index.query(Point(x, y)):
        a, b, c = floor_triangles[i]
        den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        u = ((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        v = ((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
        if u >= -1e-7 and v >= -1e-7 and u+v <= 1+1e-7:
            height = max(height, u*a[2]+v*b[2]+(1-u-v)*c[2])
    return height

def free(poly, skip=()):
    if not private.covers(poly) or public_area.intersection(poly).area > .0001:
        return False
    if entry_area.intersects(poly):
        return False
    return not any(solid_parts[i]['id'] not in skip and solids[i].distance(poly) < .12
                   for i in solid_index.query(poly.buffer(.12)))

def owner_at(center):
    return min((poly.distance(Point(center)), name) for name, poly in bodies)

# Tree roots presently intersect stair flights. Find the closest flat private
# margin; retain every trunk, canopy, branch and soil-ring part as one group.
tree_fits = []
for name in ('plaza-oak-east-root', 'garden-v4-tree-7-trunk'):
    p = parts[name]
    old = [sum(v[i] for v in p['vertices'])/len(p['vertices']) for i in (0, 1)]
    base = min(v[2] for v in p['vertices'])
    radius = .48 if 'oak' in name else .40
    candidates = []
    for dx in range(-40, 41):
        for dy in range(-40, 41):
            center = [old[0]+dx*.2, old[1]+dy*.2]
            poly = Point(center).buffer(radius)
            if not free(poly, (name,)):
                continue
            heights = [floor(center[0]+x, center[1]+y)
                       for x, y in ((0, 0), (radius, 0), (-radius, 0), (0, radius), (0, -radius))]
            if max(heights)-min(heights) > .025:
                continue
            distance, owner = owner_at(center)
            if distance > 4:
                continue
            candidates.append((math.dist(old, center)+distance*.05, center, floor(*center), owner))
    assert candidates, ('No flat private tree margin', name)
    _, center, height, owner = min(candidates)
    delta = [center[0]-old[0], center[1]-old[1], height-.015-base]
    tree_fits.append({'id': name, 'before': old, 'after': center, 'floor': height,
                     'baseBefore': base, 'baseAfter': height-.015,
                     'delta': delta, 'parcelOwner': owner})
    # Subsequent planting respects the repaired trunk footprint.
    i = next(i for i, s in enumerate(solid_parts) if s['id'] == name)
    solids[i] = Point(center).buffer(radius)
solid_index = STRtree(solids)

flowers = []
for name, p in parts.items():
    if p.get('visible', True) and re.fullmatch(r'flora-v64-\d+-soil', name):
        center = [sum(v[i] for v in p['vertices'])/len(p['vertices']) for i in (0, 1)]
        flowers.append({'group': int(name.split('-')[2]), 'center': center,
                        'outside': not private.covers(Point(center))})
bad = [f for f in flowers if f['outside']]
remaining = set(range(len(bad)))
clusters = []
while remaining:
    todo, cluster = [remaining.pop()], []
    while todo:
        i = todo.pop()
        cluster.append(bad[i])
        near = {j for j in remaining if math.dist(bad[i]['center'], bad[j]['center']) < 1.15}
        remaining -= near
        todo.extend(near)
    clusters.append(cluster)

# Sample actual parcel edges in order, including their curved corners and holes.
edges = []
for poly in (list(private.geoms) if hasattr(private, 'geoms') else [private]):
    for ring in [poly.exterior, *poly.interiors]:
        count = max(1, math.ceil(ring.length/.5))
        for i in range(count):
            at = (i+.5)/count*ring.length
            p, a, b = ring.interpolate(at), ring.interpolate((at-.05) % ring.length), ring.interpolate((at+.05) % ring.length)
            length = a.distance(b)
            if length < .001:
                continue
            tangent = [(b.x-a.x)/length, (b.y-a.y)/length]
            normal = [-tangent[1], tangent[0]]
            if not private.covers(Point(p.x+normal[0]*.2, p.y+normal[1]*.2)):
                normal = [-normal[0], -normal[1]]
            edges.append(([p.x, p.y], tangent, normal))
occupied = [Point(f['center']).buffer(.37) for f in flowers if not f['outside']]
plans = []
for cluster in sorted(clusters, key=len, reverse=True):
    group_ids = [r['group'] for r in cluster]
    component_parts = [p for name, p in parts.items() if any(
        name.startswith(f'flora-v64-{k}-') or name.startswith(f'detail-v44-flower-{k}-')
        for k in group_ids)]
    soil_points = [v for k in group_ids for v in parts[f'flora-v64-{k}-soil']['vertices']]
    bounds = [min(v[i] for v in soil_points) for i in (0, 1)] + [max(v[i] for v in soil_points) for i in (0, 1)]
    old = [(bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2]
    width_x, width_y = bounds[2]-bounds[0]+.12, bounds[3]-bounds[1]+.12
    length, width = max(width_x, width_y), min(width_x, width_y)
    old_angle = 0 if width_x >= width_y else math.pi/2
    candidates = []
    for p, tangent, normal in edges:
        center = [p[i]+normal[i]*(.43+width/2) for i in (0, 1)]
        corners = [[center[i]+tangent[i]*u*length/2+normal[i]*v*width/2 for i in (0, 1)]
                   for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        poly = Polygon(corners)
        if not free(poly) or any(poly.distance(a) < .12 for a in occupied):
            continue
        distance, owner = owner_at(center)
        if distance > 2.5:
            continue
        points = [center, *corners]
        heights = [floor(*q) for q in points]
        if max(heights)-min(heights) > .025:
            continue
        candidates.append((math.dist(old, center)+distance*.3, center, poly, owner,
                           math.atan2(tangent[1], tangent[0])-old_angle, floor(*center)))
    assert candidates, ('No house-owned flower margin', group_ids, length, width)
    _, center, poly, owner, angle, height = min(candidates, key=lambda a: a[0])
    occupied.append(poly)
    # The current floor may already cover these inherited roots. Their original
    # soil-ring datum preserves plant height while placing them on the new floor.
    old_floor = min(v[2] for v in soil_points)-.054
    plans.append({'groups': sorted(group_ids), 'parts': [p['id'] for p in component_parts],
                  'before': old, 'oldFloor': old_floor, 'after': center, 'floor': height,
                  'owner': owner, 'rotation': angle, 'footprint': list(poly.exterior.coords)[:-1]})
plan = {'source': w['source'], 'version': 73, 'flowerGroups': len(bad), 'clusters': plans,
        'treeFits': tree_fits, 'preserved': 'artwork, flower spacing, trunk/canopy geometry, town layout'}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(plan, indent=2)+'\n')
print(json.dumps({'flowerGroups': len(bad), 'clusters': len(plans), 'treeFits': tree_fits}), flush=True)
