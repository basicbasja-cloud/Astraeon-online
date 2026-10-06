"""Keep closed district curbs below existing civic and market stair treads.

The source72 curb band interpolates across discrete steps at two entrances.
The stairs supply the visible, walkable crossing there; bury the underlying
band by one tread height so its interpolated top cannot replace a stair contact.
XY topology, outlines, UVs, stair meshes and navigation metadata stay unchanged.
Run once against the saved source72 scene, before all lighting bakes.
"""
import bpy
import json
import runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('ro3_blueprint_profiles_version') == 72
assert not scene.get('ro3_stair_crossing_fit_version'), 'Crossings already fitted'
terrain = next(c for c in bpy.data.collections if c.get('family') == 'terrain')
record = json.loads(scene['ro3_blueprint_review_json'])
curbs = {r['id'] for r in record['curbs']}
fascias = {r['fascia'] for r in record['curbs']}
vertices, faces = [], []
for obj in terrain.objects:
    if obj.type != 'MESH' or obj.name in curbs or not obj.get('walkable', True):
        continue
    if obj.get('surface_role') == 'water' or not obj.get('render_visible', True):
        continue
    offset = len(vertices)
    vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
    obj.data.calc_loop_triangles()
    faces.extend(tuple(offset + i for i in f.vertices) for f in obj.data.loop_triangles)
floor = BVHTree.FromPolygons(vertices, faces, all_triangles=True)
flights = [
    {'id': 'civic-west', 'bounds': [25.1, 35.0, 27.5, 38.635]},
    {'id': 'market-west-south', 'bounds': [70.6, 65.0, 73.4, 69.0]},
]
changed = []
for obj in terrain.objects:
    if obj.name not in curbs | fascias:
        continue
    inverse = obj.matrix_world.inverted()
    count = 0
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        if not any(a-.12 <= point.x <= c+.12 and b-.12 <= point.y <= d+.12
                   for a, b, c, d in (f['bounds'] for f in flights)):
            continue
        hit = floor.ray_cast(Vector((point.x, point.y, 100)), Vector((0, 0, -1)), 150)[0]
        assert hit is not None, (obj.name, list(point))
        # Civic steps rise .175m; .22m also covers their small overlap apron.
        target = min(point.z, hit.z - .22)
        if point.z - target > .00001:
            point.z = target
            vertex.co = inverse @ point
            count += 1
    if count:
        changed.append({'id': obj.name, 'vertices': count})
assert changed, 'No curb crossing vertices found'
scene['ro3_stair_crossing_fit_version'] = 73
scene['ro3_stair_crossing_fit_json'] = json.dumps({
    'flights': flights, 'changed': changed,
    'closedXYTopologyPreserved': True, 'existingStairsSupplyCrossing': True,
    'stairGeometryAndNavigationUnchanged': True,
})
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'), compress=True)
runpy.run_path(str(ROOT / 'tools/export-world-v3.py'), run_name='__main__')
print('PASS native stair/closed-curb contact fit:', json.dumps(changed), flush=True)
