"""Narrow the oversized west lane at the Hall in the saved Wayfarer scene.

Run once after the town composition passes, then export the saved Blender file.
"""
import bpy
from pathlib import Path

root = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('layout_id') == 'wayfarer-concept-axis-v1'
assert not scene.get('hall_approach_refined'), 'Hall approach was already refined'

road = bpy.data.objects['north-residential-0']
for vertex in road.data.vertices:
    # The horizontal lane retains its junction and narrows from 2.1 to 1.4 m.
    vertex.co.y = 16 + (vertex.co.y - 16) * (1.4 / 2.1)

scene['hall_approach_refined'] = True
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'authoring/wayfarer-spatial.blend'))
print('Saved narrower Hall lane to existing Wayfarer scene')
