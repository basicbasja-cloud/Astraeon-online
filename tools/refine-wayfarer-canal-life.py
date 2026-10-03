"""Third saved-scene pass: canal bridges and visible civic route walkers."""
import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
terrain = bpy.data.collections['court-terrain']
assert scene.get('layout_id') == 'wayfarer-concept-axis-v1'
assert 'east-canal-crossing' not in bpy.data.objects, 'Canal life already refined'


def paving(name, a, b, width):
    verts = [(a[0], a[1] - width / 2, .038),
             (b[0], b[1] - width / 2, .038),
             (b[0], b[1] + width / 2, .038),
             (a[0], a[1] + width / 2, .038)]
    m = bpy.data.meshes.new(name)
    m.from_pydata(verts, [], [[0, 1, 2, 3]])
    m.update()
    o = bpy.data.objects.new(name, m)
    terrain.objects.link(o)
    o.data.materials.append(bpy.data.materials['paving'])
    o['role'] = 'decorative'
    o['shadow'] = False
    o['surface_role'] = 'residential'
    o['road_segment'] = True
    o['legacy_role'] = 'street'


def rail(name, x0, x1, y):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    c['family'] = 'fortification'
    h, w = .3, .13
    v = [(x, y + dy, z) for z in (0, h)
         for x, dy in ((x0, -w), (x1, -w), (x1, w), (x0, w))]
    m = bpy.data.meshes.new(name)
    m.from_pydata(v, [], [[0, 3, 2, 1], [4, 5, 6, 7],
                           [0, 1, 5, 4], [1, 2, 6, 5],
                           [2, 3, 7, 6], [3, 0, 4, 7]])
    m.update()
    o = bpy.data.objects.new(name + '-stone', m)
    c.objects.link(o)
    o.data.materials.append(bpy.data.materials['stoneLight'])
    o['role'] = 'solid'
    o['shadow'] = True


# The west residential lane already crosses the canal. A matching east crossing
# completes the block circulation and gives both water crossings real edges.
paving('east-canal-crossing', (27, 37.5), (36, 37.5), 2.15)
for side, x0, x1 in [('west', 21.6, 24.8), ('east', 29.2, 32.7)]:
    for edge, y in [('north', 36.25), ('south', 38.75)]:
        rail(side + '-canal-bridge-' + edge, x0, x1, y)


root = bpy.data.objects['astral-fountain-placement']
original = bpy.data.objects['plaza-pedestrian-1']
for name, kind, tint, pace, points in [
    ('south-avenue-traveller', 'travel', 112, .52,
     [(27, 42), (27, 38), (27, 34), (27, 30), (27, 34), (27, 38)]),
    ('inn-lane-patron', 'inn', 44, .44,
     [(20, 25.5), (18, 25.5), (15, 25.5), (12.8, 24), (15, 25.5)]),
    ('shrine-road-pilgrim', 'shrine', 188, .41,
     [(34, 25.5), (38, 25.5), (41, 22), (43, 16), (41, 22)]),
]:
    walker = original.copy()
    walker.name = name
    walker.parent = root
    walker.location = (0, 0, 0)
    walker['data_json'] = json.dumps({'pace': pace, 'tint': tint, 'kind': kind})
    walker['route_json'] = json.dumps([
        [x - root.location.x, y - root.location.y, 0] for x, y in points])
    bpy.data.collections['astral-fountain'].objects.link(walker)

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'))
print('Saved canal bridge pair and three town walkers')
