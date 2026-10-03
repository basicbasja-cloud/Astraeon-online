"""Restore leaf cards under their cloned canopies in the saved Wayfarer scene.

The copied trunks and canopy meshes were correctly parented to each tree's
placement empty, but the source leaf cards are children of canopy meshes.
Their parent relationship must be copied too or they remain at world origin.
"""
import bpy
from pathlib import Path

root = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('layout_id') == 'wayfarer-concept-axis-v1'
assert not scene.get('tree_hierarchy_refined'), 'Tree hierarchy already refined'

sources = {
    'plaza-oak-west': 'district-tree-0',
    'plaza-oak-east': 'district-tree-1',
    'hall-oak-west': 'district-tree-0',
    'shrine-oak-west': 'district-tree-1',
}
for clone, source in sources.items():
    for obj in bpy.data.collections[clone].objects:
        if '-leafcard-' not in obj.name:
            continue
        suffix = obj.name.removeprefix(clone + '-')
        original = bpy.data.objects[source + '-' + suffix]
        assert original.parent is not None
        obj.parent = bpy.data.objects[clone + '-' + original.parent.name.removeprefix(source + '-')]
        obj.matrix_parent_inverse = original.matrix_parent_inverse.copy()

scene['tree_hierarchy_refined'] = True
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'authoring/wayfarer-spatial.blend'))
print('Saved complete tree canopy hierarchy to existing Wayfarer scene')
