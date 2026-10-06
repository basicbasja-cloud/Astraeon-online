"""Apply public/private floor regions to saved Blender geometry, never runtime pads."""
import bpy
import json
import runpy
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('ro3_owned_planting_fit_version') == 73
assert not scene.get('ro3_public_floor_version'), 'Floor correction already authored'
plan = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
assert plan['version'] == 74
public = bpy.data.materials['publicSquareStone']
m = public.copy()
m.name = 'publicTownStone'
avenue = bpy.data.materials['avenuePaving']
avenue.diffuse_color = public.diffuse_color
avenue['texture_json'] = public['texture_json']

def world_uv(o):
    layer = o.data.uv_layers.active or o.data.uv_layers.new(name='PhysicalUV')
    for f in o.data.polygons:
        for li in f.loop_indices:
            p = o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
            layer.data[li].uv = (p.x / 8, p.y / 8)

for fit in plan['surfaces']:
    original = bpy.data.objects[fit['id']]
    template = original.copy()
    for i, region in enumerate(fit['regions']):
        o = original if i == 0 else template.copy()
        if i:
            o.name = original.name + '-private74'
            for c in original.users_collection:
                c.objects.link(o)
            # Only the original road owns the centerline/navigation annotation.
            for key in ('road_segment', 'centerline_json', 'road_width', 'legacy_role'):
                if key in o: del o[key]
        if not region.get('retainMesh'):
            inv = o.matrix_world.inverted()
            vertices = [inv @ Vector((x, y, fit['z'])) for t in region['triangles'] for x, y in t]
            mesh = bpy.data.meshes.new(o.name + '-floor74')
            mesh.from_pydata(vertices, [], [list(range(j, j + 3)) for j in range(0, len(vertices), 3)])
            o.data = mesh
        o.data.materials.clear()
        o.data.materials.append(bpy.data.materials[region['material']])
        world_uv(o)
        o['floor_zone_v74'] = region['material']
    bpy.data.objects.remove(template)
scene['ro3_public_floor_version'] = 74
scene['ro3_public_floor_json'] = json.dumps({'version': 74, 'surfaces': len(plan['surfaces']), 'removedDuplicateArea': sum(r['removedArea'] for r in plan['surfaces'])})
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'), compress=True)
runpy.run_path(str(ROOT / 'tools/export-world-v3.py'), run_name='__main__')
print('PASS saved public/private paving correction:', len(plan['surfaces']), 'floors')
