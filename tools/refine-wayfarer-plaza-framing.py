"""Fourth saved-scene pass: painted canopy framing and civic heraldry."""
import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('layout_id') == 'wayfarer-concept-axis-v1'
assert 'plaza-oak-west' not in bpy.data.collections, 'Plaza framing already refined'


def copy_tree(source, name, position):
    old = bpy.data.collections[source]
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    c['family'] = 'vegetation'
    original_root = bpy.data.objects[source + '-placement']
    root = original_root.copy()
    root.name = name + '-placement'
    root.parent = None
    root.location = position
    c.objects.link(root)
    copied = {original_root: root}
    for obj in old.objects:
        if obj.type != 'MESH':
            continue
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = name + '-' + obj.name.removeprefix(source + '-')
        c.objects.link(copy)
        copied[obj] = copy
    for obj, copy in copied.items():
        if obj == original_root:
            continue
        copy.parent = copied.get(obj.parent)
        copy.matrix_parent_inverse = obj.matrix_parent_inverse.copy()


for source, name, position in [
    ('district-tree-0', 'plaza-oak-west', (18.5, 22.2, 0)),
    ('district-tree-1', 'plaza-oak-east', (36.5, 22.4, 0)),
    ('tree-6', 'avenue-canopy-west', (17.4, 41.0, 0)),
    ('tree-7', 'avenue-canopy-east', (39.1, 41.2, 0)),
]:
    copy_tree(source, name, position)


def box(collection, name, center, size, material, role='decorative'):
    cx, cy, cz = center
    sx, sy, sz = (v / 2 for v in size)
    v = [(cx + dx * sx, cy + dy * sy, cz + dz * sz)
         for dz in (-1, 1) for dy in (-1, 1) for dx in (-1, 1)]
    m = bpy.data.meshes.new(name)
    m.from_pydata(v, [], [[0, 1, 3, 2], [4, 6, 7, 5],
                           [0, 4, 5, 1], [2, 3, 7, 6],
                           [0, 2, 6, 4], [1, 5, 7, 3]])
    m.update()
    o = bpy.data.objects.new(name, m)
    collection.objects.link(o)
    o.data.materials.append(bpy.data.materials[material])
    o['role'] = role
    o['shadow'] = role == 'solid'


def banner(name, x, y):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    c['family'] = 'fortification'
    box(c, name + '-plinth', (x, y, .17), (.46, .46, .34), 'stoneLight', 'solid')
    box(c, name + '-staff', (x, y, 1.77), (.14, .14, 3.1), 'timber')
    box(c, name + '-finial', (x, y, 3.43), (.27, .27, .27), 'gold')
    # The broad face looks toward the southern entry camera. A two-point hem,
    # gold binding, and the Consortium compass keep the world identity legible.
    m = bpy.data.meshes.new(name + '-cloth')
    m.from_pydata([(x - .52, y - .10, 3.05), (x + .52, y - .10, 3.05),
                   (x + .52, y - .10, 1.70), (x, y - .10, 1.46),
                   (x - .52, y - .10, 1.70)], [], [[0, 1, 2, 3, 4]])
    m.update()
    cloth = bpy.data.objects.new(name + '-cloth', m)
    c.objects.link(cloth)
    cloth.data.materials.append(bpy.data.materials['clothBlue'])
    cloth['role'] = 'decorative'
    cloth['shadow'] = False
    box(c, name + '-gold-hem', (x, y - .12, 2.99), (1.08, .04, .08), 'gold')
    box(c, name + '-compass-vertical', (x, y - .14, 2.38), (.09, .04, .68), 'gold')
    box(c, name + '-compass-horizontal', (x, y - .15, 2.38), (.48, .04, .09), 'gold')
    box(c, name + '-compass-core', (x, y - .17, 2.38), (.15, .05, .15), 'stoneLight')


for name, x, y in [
    ('plaza-herald-west-north', 21.3, 22.7),
    ('plaza-herald-east-north', 32.7, 22.7),
    ('plaza-herald-west-south', 22.1, 30.4),
    ('plaza-herald-east-south', 31.9, 30.4),
]:
    banner(name, x, y)

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'))
print('Saved civic trees and ASTRAEON banner framing')
