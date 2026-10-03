"""Fifth saved-scene pass: keep painterly canopies visible in gameplay views."""
import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('layout_id') == 'wayfarer-concept-axis-v1'
assert 'hall-oak-west' not in bpy.data.collections, 'Tree placement already refined'


def remove_collection(name):
    c = bpy.data.collections[name]
    for obj in list(c.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(c)


# At playable character distance selective canopy visibility made the new
# roadside trees read as bare timber; nearby authored houses already frame it.
for name in ('avenue-canopy-west', 'avenue-canopy-east'):
    remove_collection(name)

bpy.data.objects['plaza-oak-west-placement'].location = (18.0, 30.5, 0)
bpy.data.objects['plaza-oak-east-placement'].location = (36.0, 30.5, 0)


def tree(source, name, position):
    old = bpy.data.collections[source]
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    c['family'] = 'vegetation'
    original = bpy.data.objects[source + '-placement']
    root = original.copy()
    root.name = name + '-placement'
    root.parent = None
    root.location = position
    c.objects.link(root)
    copied = {original: root}
    for obj in old.objects:
        if obj.type != 'MESH':
            continue
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = name + '-' + obj.name.removeprefix(source + '-')
        c.objects.link(copy)
        copied[obj] = copy
    for obj, copy in copied.items():
        if obj == original:
            continue
        copy.parent = copied.get(obj.parent)
        copy.matrix_parent_inverse = obj.matrix_parent_inverse.copy()


tree('district-tree-0', 'hall-oak-west', (17, 13.5, 0))
tree('district-tree-1', 'shrine-oak-west', (37, 14, 0))

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'))
print('Saved clearer canopy framing to existing Wayfarer scene')
