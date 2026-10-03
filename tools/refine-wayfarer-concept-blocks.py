"""Second saved-scene pass: district density, clear axis, paired plaza canals."""
import bpy
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
terrain = bpy.data.collections['court-terrain']
assert scene.get('layout_id') == 'wayfarer-concept-axis-v1'
assert 'civic-home-west' not in bpy.data.collections, 'District blocks already refined'

# The original willow home landed in the processional route after the island
# grew. Keep the authored house and its parented apron, but form an east row.
bpy.data.objects['willow-house-placement'].location = (35.5, 39, 0)


def duplicate_building(source, name, position):
    old = bpy.data.collections[source]
    new = bpy.data.collections.new(name)
    scene.collection.children.link(new)
    new['family'] = old['family']
    old_root = bpy.data.objects[source + '-placement']
    root = old_root.copy()
    root.name = name + '-placement'
    root.parent = None
    root.location = position
    new.objects.link(root)
    for obj in old.objects:
        if obj.type != 'MESH':
            continue
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = name + '-' + obj.name.removeprefix(source + '-')
        copy.parent = root if obj.parent == old_root else None
        new.objects.link(copy)
    for obj in list(terrain.objects):
        if obj.parent != old_root:
            continue
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = name + '-' + obj.name.removeprefix(source + '-')
        copy.parent = root
        terrain.objects.link(copy)


for source, name, point in [
    ('north-house', 'civic-home-west', (20, 20.8, 0)),
    ('east-house', 'civic-shop-east', (35.5, 18.7, 0)),
    ('west-house', 'avenue-home-west', (20.5, 34, 0)),
    ('northwest-cottage', 'avenue-cottage-east', (35, 35.5, 0)),
    ('residence', 'inn-side-home', (17.5, 28.2, 0)),
    ('north-house', 'east-row-home', (40, 35, 0)),
]:
    duplicate_building(source, name, point)


def surface(name, polygon, material, role, z=.023):
    m = bpy.data.meshes.new(name)
    m.from_pydata([(x, y, z) for x, y in polygon], [], [list(range(len(polygon)))])
    m.update()
    obj = bpy.data.objects.new(name, m)
    terrain.objects.link(obj)
    obj.data.materials.append(bpy.data.materials[material])
    obj['role'] = 'decorative'
    obj['shadow'] = False
    obj['surface_role'] = role
    return obj


def stone_curb(name, a, b, width=.18, height=.15):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    nx, ny = -dy * width / (2 * length), dx * width / (2 * length)
    ring = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
            (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
    verts = [(x, y, z) for z in (0, height) for x, y in ring]
    m = bpy.data.meshes.new(name)
    m.from_pydata(verts, [], [[0, 3, 2, 1], [4, 5, 6, 7],
                              [0, 1, 5, 4], [1, 2, 6, 5],
                              [2, 3, 7, 6], [3, 0, 4, 7]])
    m.update()
    c = bpy.data.collections[name]
    o = bpy.data.objects.new(name + '-curb', m)
    c.objects.link(o)
    o.data.materials.append(bpy.data.materials['stoneLight'])
    o['role'] = 'solid'
    o['shadow'] = True


# Two curved runs of water echo the approved art's canal-framed civic walk.
# The shallow masonry gives each waterline a credible contact with the street.
for side, polygon in [
    ('west', [(22.0, 30.5), (23.7, 30.0), (24.3, 32.8),
              (24.1, 37.5), (23.7, 41.4), (22.8, 44.4),
              (21.6, 43.8), (22.2, 40.0), (22.4, 36.4)]),
    ('east', [(30.3, 30.0), (32.0, 30.5), (31.6, 36.4),
              (31.8, 40.0), (32.4, 43.8), (31.2, 44.4),
              (30.3, 41.4), (29.9, 37.5), (29.7, 32.8)]),
]:
    surface(side + '-civic-canal', polygon, 'water', 'water')
    edges = ([(23.7, 30.0), (24.3, 32.8), (24.1, 37.5),
              (23.7, 41.4), (22.8, 44.4)] if side == 'west' else
             [(30.3, 30.0), (29.7, 32.8), (29.9, 37.5),
              (30.3, 41.4), (31.2, 44.4)])
    for index, (a, b) in enumerate(zip(edges, edges[1:])):
        collection = bpy.data.collections.new(side + '-canal-curb-' + str(index))
        scene.collection.children.link(collection)
        collection['family'] = 'fortification'
        stone_curb(collection.name, a, b)

# Paved transition between circular plaza and the long southern avenue.
surface('south-plaza-throat', [(24.3, 29.3), (29.7, 29.3),
                              (30, 33.2), (24, 33.2)], 'paving', 'forecourt', .016)

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'))
print('Saved denser concept blocks and paired canals to existing Wayfarer scene')
