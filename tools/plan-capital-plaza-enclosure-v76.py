"""Bring four existing plaza fronts into a walkable, inhabited square edge.

Plans whole-model translations and continuous property contacts from the actual
export. It does not change the world or its native source.
"""
import json, math, hashlib, copy, argparse, runpy
from pathlib import Path
from shapely.geometry import Polygon, MultiPoint, LineString, Point, box
from shapely.affinity import translate
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
from shapely.geometry.polygon import orient

R = Path(__file__).resolve().parents[1]
O = R / 'docs/review/wayfarer-capital-v76/property-frontages'
raw = (R / 'world/v3/wayfarer-spatial.json').read_bytes()
s = json.loads(raw)
p = json.loads((O.parent / 'native-plan.json').read_text())
ap=argparse.ArgumentParser();ap.add_argument('--further-inset',action='store_true');args=ap.parse_args()
previous=p.get('plazaEnclosureRefinement')
assert bool(previous)==args.further_inset,'First inset or one further correction only'
assert not previous or previous.get('iteration',1)==1,'Further correction already applied'
step=6 if previous else 10
objects = {o['id']: o for o in s['objects']}
names = {'capital-residential-040-b': step, 'capital-residential-052-b': step,
         'capital-residential-028-b': -step, 'capital-workshop-032-b': -step}
roads = unary_union([LineString(r['centerline']).buffer(r['width']/2,
    cap_style=2, join_style=2) for r in p['roads']])
outlines = {l['id']: MultiPoint([v[:2] for a in objects[l['id']]['parts']
    if a.get('visible', True) for v in a['vertices']]).convex_hull for l in p['lots']}
moves = []
for name, dx in names.items():
    lot = next(l for l in p['lots'] if l['id'] == name)
    before = lot['center'][:]
    outlines[name] = translate(outlines[name], dx, 0)
    lot['center'][0] += dx
    lot['lot'] = [[x+dx, y] for x, y in lot['lot']]
    moves.append({'id': name, 'before': before, 'after': lot['center'][:], 'delta': [dx, 0, 0]})
    # A planning copy permits independent clearance against the retained city.
    owner = copy.deepcopy(objects[name])
    for a in owner['parts']:
        for v in a['vertices']: v[0] += dx
    objects[name] = owner
for name in names:
    q = outlines[name]
    assert q.intersection(roads.buffer(.12)).area < .001, (name, 'street')
    assert min(q.distance(v) for n, v in outlines.items() if n != name) > .74, name
    for owner in objects.values():
        if owner['id'] in outlines: continue
        for a in owner['parts']:
            if a['role'] == 'solid':
                assert q.distance(MultiPoint([v[:2] for v in a['vertices']]).convex_hull) > .20, (name, a['id'])

def region(parts):
    return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])

def mesh(poly, z):
    vertices, faces, index = [], [], {}
    for t in constrained_delaunay_triangles(poly).geoms:
        points = list(t.exterior.coords)[:-1]
        if not t.exterior.is_ccw: points.reverse()
        f = []
        for x, y in points:
            key = (round(x, 5), round(y, 5))
            if key not in index: index[key] = len(vertices); vertices.append([*key, z])
            f.append(index[key])
        faces.append(f)
    return {'vertices': vertices, 'faces': faces}

private_parts = [a for a in p['floors'] if a['material'] == 'houseApronPaving'
                 and all(abs(v[2]-.04) < .00001 for v in a['vertices'])]
old_private = region(private_parts)
extra=6 if previous else 0
patches = [box(101, 129.1, 114.1+extra, 137.5), box(100, 150.5, 113.1+extra, 159.1),
           box(142.7-extra, 129.1, 155.7, 137.5), box(142.9-extra, 150.5, 155.9, 159.1)]
extension = unary_union(patches).difference(old_private)
assert extension.intersection(roads).area < .001
private = unary_union([old_private, extension])
edited = []
floors = []
for a in p['floors']:
    if a['id'].startswith('capital-owned-curb-'): continue
    if a['material'] == 'publicTownStone':
        q = region([a]); hit = q.intersection(extension).area
        if hit > .000001:
            edited.append(a['id'])
            q = q.difference(extension)
            if q.area < .000001: continue
            a = {**a, **mesh(q, .025)}
    floors.append(a)
for i, q in enumerate(patches):
    q = q.difference(old_private)
    floor_id=f'capital-private-plaza-edge-2-{i}' if previous else f'capital-private-plaza-edge-{i}'
    floors.append({'id': floor_id, 'material': 'houseApronPaving',
                   'role': 'yard', **mesh(q, .04)})
loops, blocks = [], []
for i, q in enumerate(private.geoms if hasattr(private, 'geoms') else [private]):
    q = orient(q, sign=1)
    blocks.append({'outer': list(q.exterior.coords)[:-1], 'holes': [list(r.coords)[:-1] for r in q.interiors]})
    loops.extend([list(q.exterior.coords)[:-1], *[list(r.coords)[:-1] for r in q.interiors]])
    floors.append({'id': f'capital-owned-curb-{i}', 'material': 'roadCurbStone',
                   'role': 'forecourt', **mesh(q.difference(q.buffer(-.22, join_style=2)), .20)})
public = region([a for a in floors if a['material'] == 'publicTownStone'])
assert public.intersection(private).area < .001
assert region([a for a in p['floors'] if a['material'] == 'publicTownStone']).symmetric_difference(public.union(extension)).area < .001

# Retain all existing planted pieces except where the moved physical fronts or
# their entrances require clearance. Add curved pockets on the new property edge.
old_lawns = json.loads((O/'natural-lawns-plan.json').read_text())
entries, feet, props = [], [], []
for l in p['lots']:
    heading = l['angle'] + l.get('frontageOffset', 0)
    normal = (-math.sin(heading), math.cos(heading))
    for a in objects[l['id']]['parts']:
        if not a['id'].endswith('-door-leaf'): continue
        center = [sum(v[i] for v in a['vertices'])/len(a['vertices']) for i in (0, 1)]
        entries.append(LineString([center, [center[i]+normal[i]*4.2 for i in (0, 1)]]).buffer(1.1, cap_style=2))
for o in objects.values():
    if o['id'] == 'capital-beta-frontage-groundcover': continue
    for a in o['parts']:
        if a['role'] == 'solid' and min(v[2] for v in a['vertices']) < 1:
            footprint=MultiPoint([v[:2] for v in a['vertices']]).convex_hull
            # Sixteen-sided rounded contacts remain outside the original .20
            # clearance (the minimum radius is .21*cos(pi/16) > .20).
            feet.append(footprint.buffer(.21,quad_segs=4) if previous else footprint.buffer(.20))
        low = [v[:2] for v in a['vertices'] if v[2] < 1.05]
        if len(low) >= 3 and a['material'] not in ('grass', 'leaf', 'flowerRose', 'vergeGroundcover', 'vergeGroundcoverShade'):
            footprint=MultiPoint(low).convex_hull
            props.append(footprint.buffer(.126,quad_segs=4) if previous else footprint.buffer(.12))
keepout = unary_union(entries + feet + props + [roads.buffer(.12)])
green = region(old_lawns['pieces']).difference(keepout)
for i, q in enumerate(patches):
    samples = [Point(q.exterior.interpolate(j/30*q.length)).buffer(1.3+.25*math.sin(j*.4+i), quad_segs=6) for j in range(30)]
    green = green.union(unary_union(samples).intersection(q.buffer(-.18)).difference(keepout))
green = green.intersection(private).simplify(.045, preserve_topology=True).difference(keepout)
pieces = []
for i, q in enumerate(green.geoms if hasattr(green, 'geoms') else [green]):
    if q.area < .8: continue
    block = next(j for j, b in enumerate(blocks) if Polygon(b['outer'], b['holes']).buffer(.0001).covers(q))
    pieces.append({'id': f'plaza-edge-lawn-{i:03}', 'block': block, 'material': 'grass', 'area': q.area, **mesh(q, .047)})
assert sum(len(q['faces']) for q in pieces) < 12500,sum(len(q['faces']) for q in pieces)
new_lawns = {**old_lawns, 'pieces': pieces, 'area': sum(q['area'] for q in pieces),
             'triangles': sum(len(q['faces']) for q in pieces), 'plazaEnclosureRevision': True,
             'previousCandidateArea': old_lawns['area']}
pre_feather_lawns=None
if previous:
    new_lawns['contactTessellation']={'quadSegments':4,'footRadius':.21,'propRadius':.126,
        'minimumFootRadius':.21*math.cos(math.pi/16),'retainedFootClearance':.20,
        'minimumPropRadius':.126*math.cos(math.pi/16),'retainedPropClearance':.12,
        'unfeatheredTriangleBudget':12500}
    new_lawns.pop('nativeEdgeOpacity',None);new_lawns.pop('edgeBlending',None)
    pre_feather_lawns=copy.deepcopy(new_lawns)
    new_lawns=runpy.run_path(str(R/'tools/plan-capital-grass-feather-v76.py'))['feather_plan'](new_lawns)
old_patrol = next(a for o in s['objects'] for a in o.get('walkers', []) if a['id'] == 'capital-resident-12')
patrol = copy.deepcopy(old_patrol)
for q in patrol['route']:
    if q[0] in (108,116): q[0] = 120 if previous else 116
    elif q[0] in (149,140): q[0] = 138 if previous else 140
revision = {'beforeSourceSHA256': hashlib.sha256(raw).hexdigest(), 'moves': moves,
            'editedPublicFloors': edited, 'privateExtensionArea': extension.area,
            'privateExtensions': [list(q.exterior.coords)[:-1] for q in patches],
            'retainedRoadWidths': {r['id']: r['width'] for r in p['roads']},
            'walker': {'id': patrol['id'], 'before': old_patrol, 'after': patrol},
            'purpose': 'Closer plaza-facing fronts, joined private terraces, clear entrances and ceremonial spokes'}
revision.update(iteration=2 if previous else 1,targetInset=16 if previous else 10)
if previous:
    revision['iterationMoves']=copy.deepcopy(moves)
    initial={m['id']:m for m in previous['moves']}
    for m in moves:
        m['before']=initial[m['id']]['before'];m['delta'][0]+=initial[m['id']]['delta'][0]
    revision['privateExtensionArea']+=previous['privateExtensionArea']
    revision['walker']['iterationBefore']=revision['walker']['before']
    revision['walker']['before']=previous['walker']['before']
    revision['previousRevision']=previous
plaza_area=region([a for a in floors if a['id']=='capital-royal-plaza']).area
public_area=region([a for a in floors if a['material']=='publicTownStone' and a['id']!='capital-royal-plaza']).area
revision['areaAccounting']={'beforePrivate':p['privateArea'],'beforePublicExcludingPlaza':p['publicArea'],
    'afterPrivate':private.area,'afterPublicExcludingPlaza':public_area,'afterPlaza':plaza_area}
p.update(privateArea=private.area,publicArea=public_area,plazaArea=plaza_area)
p.update(floors=floors, privateLoops=loops, ownedBlocks=blocks, plazaEnclosureRefinement=revision)
(O/'plaza-enclosure-plan.json').write_text(json.dumps({'revision': revision, 'plan': p, 'lawns': new_lawns,
    'preFeatherLawns':pre_feather_lawns}, separators=(',', ':'))+'\n')
print(json.dumps(revision, indent=2))
