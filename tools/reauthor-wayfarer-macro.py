"""Recompose the saved Golden Wayfarer town without rebuilding its authored assets.

Run once on authoring/wayfarer-spatial.blend, then export that saved scene. The
district assemblies, textured presentation, services, portals, and walkers stay
in Blender; this pass changes their town-scale placement and connective tissue.
"""
import bpy
import json
import math
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
kit = runpy.run_path(str(ROOT / 'tools/blender-v3-kit.py'))
mesh = kit['mesh']
family = kit['family']
scene = bpy.context.scene
terrain = bpy.data.collections['court-terrain']
assert scene.get('layout_id') != 'wayfarer-concept-axis-v1', 'Concept axis already authored'


def lerp(value, stops):
    for (a, av), (b, bv) in zip(stops, stops[1:]):
        if value <= b:
            return av + (value - a) * (bv - av) / (b - a)
    a, av = stops[-2]
    b, bv = stops[-1]
    return av + (value - a) * (bv - av) / (b - a)


def mapped(x, y):
    return (lerp(x, [(3, 4), (8, 8), (13.5, 13), (21.8, 27),
                     (30, 42), (40.3, 53)]),
            lerp(y, [(3.5, 3), (12.7, 10), (19.2, 25.5),
                     (26.3, 35), (36.8, 46.5)]))


placements = {
    'caravan-gate': (28.05, 45.5),
    'guild-hall': (27, 10),
    'astral-fountain': (27, 25.5),
    'east-inn': (11, 20),
    'artisan-workshop': (13, 35),
    'moon-shrine': (43, 11.5),
    'market-shop': (42, 24.0),
    'east-house': (49, 20.5),
    'north-gate': (27.66, 4.7),
    'north-garden-house': (12.5, 8.5),
    'northwest-cottage': (8.5, 13),
    'residence': (17, 37),
    'willow-house': (29, 37),
    'north-house': (45, 38),
    'west-house': (49, 32.5),
    'bench-a': (21, 29.5),
    'bench-b': (33, 29.5),
    'guild-board': (31, 13.5),
    'planter-a': (23, 13.2),
    'planter-b': (31, 13.2),
    'caravan-cart': (45, 32),
    'east-cart': (12, 29),
}

original = {}
for collection in bpy.data.collections:
    if collection.get('family') in ('terrain', None) or collection.name.startswith('town-wall-'):
        continue
    root = bpy.data.objects.get(collection.name + '-placement')
    if root:
        old = tuple(root.location[:2])
        target = placements.get(collection.name, mapped(*old))
        original[collection.name] = (old, target)
        root.location.x, root.location.y = target

# The former minor south post is superseded by the existing monumental gate.
old_south = bpy.data.collections.get('south-gate')
if old_south:
    for obj in list(old_south.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old_south)

# This gate assembly already carries the bridge, heraldry and Goldenfield
# transition. Keep its hierarchy, with the keeper beside the new entrance.
keeper = bpy.data.objects['gatekeeper']
keeper.location.x = -2.6
keeper.location.y = -2.3

# Preserve the sculpted island ground topology and its existing vertical faces,
# while placing its 18-point perimeter around the re-spaced districts.
perimeter = [
    (6, 27), (4, 18), (7, 8), (16, 4), (24, 4), (27, 3),
    (30, 4), (39, 4), (51, 8), (53, 23), (53, 40),
    (42, 46), (29.3, 46), (27, 47.5), (24.7, 46),
    (12, 45), (6, 37), (9, 27),
]
ground = bpy.data.objects['court-ground']
assert len(ground.data.vertices) == len(perimeter) * 2
for index, vertex in enumerate(ground.data.vertices):
    vertex.co.x, vertex.co.y = perimeter[index % len(perimeter)]
ground.data.update()
scene['world_bounds_json'] = json.dumps({'minX': 0, 'minY': 0, 'maxX': 56, 'maxY': 64})


def move_surface(obj, dx, dy):
    obj.location.x += dx
    obj.location.y += dy


def move_like(obj, assembly):
    old, target = original[assembly]
    move_surface(obj, target[0] - old[0], target[1] - old[1])


for obj in list(terrain.objects):
    if obj == ground or obj.name == 'western-water':
        continue
    # Contact paving parented to an assembly has already followed its root.
    # Moving it again would detach the painted apron from the building.
    if obj.parent is not None:
        continue
    if obj.get('road_segment') or obj.name.startswith('street-junction-'):
        bpy.data.objects.remove(obj, do_unlink=True)
        continue
    name = obj.name
    if name == 'field-road-bank':
        bpy.data.objects.remove(obj, do_unlink=True)
    elif name == 'west-arrival-bridge-surface':
        move_like(obj, 'caravan-gate')
    elif name.startswith('plaza-') or name == 'orientation-plaza':
        move_like(obj, 'astral-fountain')
    elif name.startswith('civic-') or name.startswith('guild-hall-'):
        move_like(obj, 'guild-hall')
    elif name.startswith('shrine-') or name == 'moon-shrine-forecourt' or name == 'shrine-garden':
        move_like(obj, 'moon-shrine')
    elif name == 'market-browsing':
        move_surface(obj, 11, 3)
    elif name == 'forge-workyard':
        move_like(obj, 'artisan-workshop')
    elif name == 'inn-courtyard':
        move_like(obj, 'east-inn')
    elif name == 'arrival-forecourt':
        move_like(obj, 'caravan-gate')
    elif name == 'west-public-green':
        move_surface(obj, 1, 3)
    elif name == 'south-public-green':
        move_surface(obj, 6, 10)
    elif name == 'domestic-garden':
        move_surface(obj, 4, 7)
    else:
        prefix = name.removesuffix('-forecourt')
        for assembly in original:
            if name.startswith(assembly + '-') or prefix == assembly:
                move_like(obj, assembly)
                break
        else:
            old_center = obj.matrix_world.translation
            nx, ny = mapped(old_center.x, old_center.y)
            move_surface(obj, nx - old_center.x, ny - old_center.y)


def surface(name, points, material='paving', role='forecourt'):
    obj = mesh(terrain, name, [(x, y, .012) for x, y in points],
               [list(range(len(points)))], material, 'decorative', False)
    obj['surface_role'] = role
    return obj


def road(name, points, width, role='residential'):
    for index, (a, b) in enumerate(zip(points, points[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        nx, ny = -dy * width / (2 * length), dx * width / (2 * length)
        obj = surface(name + '-' + str(index), [
            (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
            (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)],
            role=role)
        obj.data.polygons[0].flip()  # the left-bank-first ring faces down
        for vertex in obj.data.vertices:
            vertex.co.z = .032  # street paving clears the existing green infill
        obj['road_segment'] = True
        obj['legacy_role'] = ('avenue' if role == 'primary' else
                              'street' if role == 'residential' else role)


# A broad, legible plaza and actual approach routes replace the prior narrow
# west-entry network. Side lanes make the district blocks readable from above.
plaza = bpy.data.objects['orientation-plaza']
center = (27, 25.5)
for v in plaza.data.vertices:
    v.co.x = center[0] + (v.co.x - 21.8) * 1.2
    v.co.y = center[1] + (v.co.y - 19.2) * 1.18
plaza.location.x = plaza.location.y = 0

road('south-civic-avenue', [(27, 46), (27, 33), (27, 30)], 3.5, 'primary')
road('north-civic-avenue', [(27, 21), (27, 16.0)], 3.2, 'primary')
road('market-street', [(33.5, 25.5), (41, 25.5), (49.5, 25.5)], 2.8)
road('inn-street', [(20.5, 25.5), (13, 25.5), (11, 23)], 2.7)
road('forge-street', [(13, 25.5), (13, 35.5), (20, 37.5)], 2.3)
road('shrine-lane', [(38, 25.5), (43, 20), (43, 15)], 2.2)
road('north-residential', [(27, 16), (17, 16), (12, 14)], 2.1)
road('northwest-lane', [(17, 16), (14, 10), (21, 8)], 1.7)
road('east-residential', [(47, 25.5), (47, 34), (44, 38), (33, 38)], 2.1)
road('south-residential', [(27, 37.5), (20, 37.5), (13, 35.5)], 2.0)
road('plaza-market-loop', [(34, 30), (39, 31.5), (47, 31.5)], 1.8)
road('north-gate-lane', [(27, 16), (27, 5.8), (27, 2.8)], 1.6)
road('south-bridge-road', [(27, 48), (27, 54), (26.5, 62)], 2.2, 'primary')

# Irregular opposite bank closes the bridge composition with walkable ground.
surface('goldenfield-bank', [
    (16, 53), (22, 52.5), (26, 52.9), (30, 52.2), (37, 54),
    (39, 60), (35, 65), (17, 65), (14, 60)], 'grass', 'green')

# Old wall pieces followed the compressed island. Re-use their authored stone
# material and role, with openings at both portal routes.
for collection in list(bpy.data.collections):
    if not collection.name.startswith('town-wall-'):
        continue
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)

wall_paths = [
    [(6, 27), (4, 18), (7, 8), (16, 4), (24.6, 4)],
    [(29.4, 4), (39, 4), (51, 8), (53, 23), (53, 40),
     (42, 46), (29.3, 46)],
    [(24.7, 46), (12, 45), (6, 37), (9, 27)],
]
index = 0
for path in wall_paths:
    for a, b in zip(path, path[1:]):
        collection = family('town-wall-' + str(index), 'fortification')
        index += 1
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        nx, ny = -dy * .18 / length, dx * .18 / length
        poly = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        verts = [(x, y, z) for z in (0, .95) for x, y in poly]
        mesh(collection, collection.name + '-masonry', verts,
             [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
              [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]],
             'stone', 'solid', True)

scene['spawn_json'] = json.dumps([27, 47.1, 0])
scene['safe_spawn_json'] = json.dumps([27, 32.5, 0])
scene['route_json'] = json.dumps([
    {'name': 'Arrival', 'position': [27, 47.1]},
    {'name': 'South avenue', 'position': [27, 36]},
    {'name': 'Plaza', 'position': [27, 29]},
    {'name': 'Hall', 'position': [27, 15.5]},
    {'name': 'Market', 'position': [41, 26]},
    {'name': 'Blacksmith', 'position': [13, 31.5]},
    {'name': 'Inn', 'position': [11.5, 23.5]},
    {'name': 'Residential', 'position': [30, 38]},
    {'name': 'Shrine', 'position': [43, 16]},
])
scene['districts_json'] = json.dumps([
    {'name': 'Consortium Hall', 'x': 27, 'y': 10},
    {'name': 'Wayfarer Plaza', 'x': 27, 'y': 25.5},
    {'name': 'Lantern Market', 'x': 43, 'y': 25},
    {'name': 'Bronze Anvil', 'x': 13, 'y': 35},
    {'name': 'Seafarer Rest', 'x': 11, 'y': 20},
    {'name': 'Moon Shrine', 'x': 43, 'y': 11.5},
    {'name': 'Willow Quarter', 'x': 34, 'y': 38},
    {'name': 'South Arrival', 'x': 27, 'y': 45},
])
scene['layout_id'] = 'wayfarer-concept-axis-v1'

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'))
print('Saved concept-axis macro reauthoring to the existing Wayfarer scene')
