"""Plan street-facing original house envelopes and infill in the saved town.

RO3 street references favor adjoining frontages, leaving civic/gate squares
open. Growth/infill respects existing roads, service access and patrol legs.
This emits a reviewable plan; it never edits terrain or runtime saves.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def hull(points):
    points = sorted(set(tuple(p[:2]) for p in points))
    cross = lambda a, b, c: (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    lower, upper = [], []
    for target, values in ((lower, points), (upper, reversed(points))):
        for p in values:
            while len(target) > 1 and cross(target[-2], target[-1], p) <= 0:
                target.pop()
            target.append(p)
    return lower[:-1] + upper[:-1]


def inside(p, poly):
    result = False
    for a, b in zip(poly, poly[-1:] + poly[:-1]):
        if (a[1] > p[1]) != (b[1] > p[1]) and p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]:
            result = not result
    return result


def distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def overlap(a, b, margin=0):
    for poly in (a, b):
        for p, q in zip(poly, poly[1:] + poly[:1]):
            dx, dy = q[0] - p[0], q[1] - p[1]
            length = math.hypot(dx, dy)
            if length < 1e-8:
                continue
            project = lambda v: (v[0] * dy - v[1] * dx) / length
            av, bv = [project(v) for v in a], [project(v) for v in b]
            if max(av) + margin < min(bv) or max(bv) + margin < min(av):
                return False
    return True


def segment_overlap(poly, a, b, radius):
    if inside(a, poly) or inside(b, poly):
        return True
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length < 1e-8:
        return min(distance(a, p, q) for p, q in zip(poly, poly[1:] + poly[:1])) < radius
    n = (-dy / length * radius, dx / length * radius)
    capsule = [(a[0] + n[0], a[1] + n[1]), (b[0] + n[0], b[1] + n[1]),
               (b[0] - n[0], b[1] - n[1]), (a[0] - n[0], a[1] - n[1])]
    return overlap(poly, capsule) or min(distance(v, a, b) for v in poly) < radius


def rectangle(center, tangent, normal, width, depth):
    return [(center[0] + tangent[0] * x + normal[0] * y,
             center[1] + tangent[1] * x + normal[1] * y)
            for x, y in ((-width / 2, -depth / 2), (width / 2, -depth / 2),
                         (width / 2, depth / 2), (-width / 2, depth / 2))]


def plan(world, max_added):
    roads = [hull(s['vertices']) for s in world['terrain']['surfaces'] if s.get('centerline') and s.get('width', 0) >= 1.8]
    patrols, services, static = [], [], []
    houses = []
    for obj in world['objects']:
        if obj['id'].startswith('ro3-infill-'):
            continue
        for actor in obj.get('walkers', []):
            route = actor['route']
            patrols += list(zip(route, route[1:] + route[:1]))
        services += [s['position'][:2] for s in obj.get('services', [])]
        for p in obj['parts']:
            if p['role'] == 'solid' and obj['family'] != 'vegetation' and not p['id'].startswith('ro3-v68-'):
                static.append((obj['id'], p['id'], hull(p['vertices'])))
        if obj['id'].startswith('frontage-') or obj['family'] not in ('residential', 'market', 'workshop', 'inn'):
            continue
        walls = [p for p in obj['parts'] if p['role'] == 'solid' and p['id'].endswith('-walls')]
        if not walls:
            continue
        wall = max(walls, key=lambda p: (max(v[2] for v in p['vertices']) - min(v[2] for v in p['vertices'])))
        doors = [p for p in obj['parts'] if p['id'].endswith(('-door', '-door-leaf')) and 'wing' not in p['id']]
        if not doors:
            continue
        door = min(doors, key=lambda p: len(p['vertices']))
        dcenter = [sum(v[i] for v in door['vertices']) / len(door['vertices']) for i in (0, 1)]
        poly = hull(wall['vertices'])
        a, b = min(zip(poly, poly[1:] + poly[:1]), key=lambda edge: distance(dcenter, *edge))
        length = math.dist(a, b)
        normal = ((b[1] - a[1]) / length, -(b[0] - a[0]) / length)
        tangent = (normal[1], -normal[0])
        xs = [v[0] * tangent[0] + v[1] * tangent[1] for v in poly]
        ys = [v[0] * normal[0] + v[1] * normal[1] for v in poly]
        center_x, front_y = (min(xs) + max(xs)) / 2, max(ys)
        width, depth = max(xs) - min(xs), max(ys) - min(ys)
        houses.append({'owner': obj['id'], 'family': obj['family'], 'wall': wall['id'],
            'tangent': tangent, 'normal': normal, 'centerProjection': center_x,
            'frontProjection': front_y, 'oldWidth': width, 'oldDepth': depth,
            'oldTop': max(v[2] for v in wall['vertices']), 'oldBase': min(v[2] for v in wall['vertices']),
            'originalPolygon': poly})
    accepted = []
    land = world['terrain']['walkablePolygon']

    def clear(poly, owner=None, existing=False):
        if not all(inside(p, land) for p in poly):
            return False
        if any(overlap(poly, road, .12) for road in roads):
            return False
        if any(segment_overlap(poly, a, b, .45) for a, b in patrols):
            return False
        if any(inside(p, poly) or min(distance(p, a, b) for a, b in zip(poly, poly[1:] + poly[:1])) < .75 for p in services):
            return False
        if any(oid != owner and overlap(poly, p, .30) for oid, _, p in static):
            return False
        if any(other['owner'] != owner and overlap(poly, other['polygon'], .40) for other in accepted):
            return False
        return True

    for index, house in enumerate(sorted(houses, key=lambda h: h['owner'])):
        target_w = max(house['oldWidth'], 7.2 if house['family'] == 'inn' else 6.4 if house['family'] == 'workshop' else 5.8)
        target_d = max(house['oldDepth'], 5.2 if house['family'] == 'inn' else 4.6)
        house['physicalMode'] = 'retain traced ground footprint'
        for fraction in (1, .8, .6, .4, .2, 0):
            w = house['oldWidth'] + (target_w - house['oldWidth']) * fraction
            d = house['oldDepth'] + (target_d - house['oldDepth']) * fraction
            n, t = house['normal'], house['tangent']
            cy = house['frontProjection'] - d / 2
            center = (t[0] * house['centerProjection'] + n[0] * cy, t[1] * house['centerProjection'] + n[1] * cy)
            poly = rectangle(center, t, n, w + .22, d + .22)
            if clear(poly, house['owner'], True):
                house.update(width=w, depth=d, center=center, polygon=poly, physicalMode='expanded rectangular envelope')
                break
        else:
            # Keep the original occupied ground if paths prevent a larger box.
            # The taller upper floor/roof may jetty above it, like the reference.
            n, t = house['normal'], house['tangent']
            cy = house['frontProjection'] - house['oldDepth'] / 2
            center = (t[0] * house['centerProjection'] + n[0] * cy, t[1] * house['centerProjection'] + n[1] * cy)
            house.update(width=house['oldWidth'], depth=house['oldDepth'], center=center, polygon=house['originalPolygon'])
        house['index'] = index
        accepted.append(house)

    # Coherent rows on the main approach and connected neighbourhood streets.
    # Preserve the fountain/Hall/gate breathing spaces seen in the references.
    streets = [('approach', (54, 64), (54, 81), 8),
               ('western', (28, 49), (28, 78), 5.5),
               ('willow', (30, 80), (90, 80), 5.5),
               ('eastern', (90, 32), (90, 76), 5.5),
               ('garden', (28, 32.5), (88, 32.5), 1.8)]
    infill = []
    for street, a, b, road_width in streets:
        length = math.dist(a, b)
        along = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        side_normal = (-along[1], along[0])
        for sign in (-1, 1):
            # Test closely spaced fronts instead of isolated random placements.
            for step in range(int(length / 1.5) + 1):
                q = (a[0] + along[0] * step * 1.5, a[1] + along[1] * step * 1.5)
                for setback in (.25, .65, 1.4, 2.2, 3.0):
                    width, depth = 5.8, 4.6
                    n = (-side_normal[0] * sign, -side_normal[1] * sign)
                    t = (n[1], -n[0])
                    offset = road_width / 2 + setback + depth / 2
                    center = (q[0] + side_normal[0] * sign * offset, q[1] + side_normal[1] * sign * offset)
                    if center[1] < 42 and 41 < center[0] < 68:
                        continue
                    if math.dist(center, (54, 51)) < 13:
                        continue
                    if not (15 < center[0] < 104 and 15 < center[1] < 85):
                        continue
                    poly = rectangle(center, t, n, width + .22, depth + .22)
                    if not clear(poly):
                        continue
                    record = {'owner': 'ro3-infill-' + street + '-' + str(len(infill) + 1),
                        'street': street, 'family': 'market' if len(infill) % 3 == 0 else 'residential',
                        'width': width, 'depth': depth, 'center': center, 'normal': n, 'tangent': t,
                        'polygon': poly, 'setback': setback, 'index': len(infill), 'physicalMode': 'new street frontage'}
                    accepted.append(record)
                    infill.append(record)
                    break
                if len(infill) >= max_added:
                    break
            if len(infill) >= max_added:
                break
        if len(infill) >= max_added:
            break
    return {'version': 68, 'reference': 'RO3 04_08_00 / 04_08_39 / 04_08_45 street enclosure; preserve civic/gate squares',
        'existingEnvelopeCount': len(houses), 'infillCount': len(infill),
        'protected': ['existing road polygons', 'service access', 'patrol legs', 'other solid footprints', 'fountain/Hall/gate breathing space'],
        'existingEnvelopes': houses, 'infill': infill}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT / 'world/v3/wayfarer-spatial.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-added', type=int, default=18)
    args = parser.parse_args()
    result = plan(json.loads(args.source.read_text()), args.max_added)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('Planned', result['existingEnvelopeCount'], 'existing envelopes and', result['infillCount'], 'street-facing additions')
