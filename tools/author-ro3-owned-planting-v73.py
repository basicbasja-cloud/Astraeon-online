"""Apply the reviewed private-margin plan to whole native plant groups."""
import bpy
import json
import runpy
import sys
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('ro3_stair_crossing_fit_version') == 73
assert not scene.get('ro3_owned_planting_fit_version'), 'Planting already fitted'
plan = json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
assert plan['version'] == 73
for fit in plan['treeFits']:
    if fit['id'] == 'plaza-oak-east-root':
        objects = set(bpy.data.collections['plaza-oak-east'].objects)
    else:
        objects = {o for o in bpy.data.objects if 'garden-v4-tree-7-' in o.name}
    assert objects
    for obj in objects:
        if obj.parent not in objects:
            obj.matrix_world = Matrix.Translation(Vector(fit['delta'])) @ obj.matrix_world
    bpy.context.view_layer.update()
for fit in plan['clusters']:
    transform = (Matrix.Translation(Vector((*fit['after'], fit['floor']))) @
                 Matrix.Rotation(fit['rotation'], 4, 'Z') @
                 Matrix.Translation(Vector((-fit['before'][0], -fit['before'][1], -fit['oldFloor']))))
    root = bpy.data.objects[fit['owner']+'-placement']
    for name in fit['parts']:
        obj = bpy.data.objects[name]
        matrix = transform @ obj.matrix_world
        obj.parent = root
        obj.matrix_world = matrix
        obj['planting_owner_v73'] = fit['owner']
    bpy.context.view_layer.update()
scene['ro3_owned_planting_fit_version'] = 73
scene['ro3_owned_planting_fit_json'] = json.dumps(plan)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'), compress=True)
runpy.run_path(str(ROOT / 'tools/export-world-v3.py'), run_name='__main__')
print('PASS whole native groups rehomed:', plan['flowerGroups'], 'flowers;', len(plan['treeFits']), 'trees', flush=True)
