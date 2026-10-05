"""Read-only geometric check for trim crossing the new nine-light windows.

Cast outward through each pane center against the other visible architecture
in that lot. This caught the small dormers inheriting full-size knee braces.
Run inside Blender on saved source68; does not save or alter geometry.
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

assert bpy.context.scene.get('ro3_facade_version') == 68
checks, failures = [], []
for collection in bpy.data.collections:
    if not any(o.name.startswith('ro3-v68-') and o.name.endswith('-glass') for o in collection.objects):
        continue
    vertices, triangles, owners = [], [], []
    for obj in collection.objects:
        if obj.type != 'MESH' or not obj.get('render_visible', True):
            continue
        if obj.data.materials[0].name == 'frontageGlazing':
            continue
        base = len(vertices)
        vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        obj.data.calc_loop_triangles()
        for face in obj.data.loop_triangles:
            triangles.append(tuple(base + i for i in face.vertices))
            owners.append(obj.name)
    tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True)
    for obj in collection.objects:
        if not obj.name.startswith('ro3-v68-') or not obj.name.endswith('-glass'):
            continue
        root = obj.parent
        normal = (Vector((0, -1, 0)) if '-rear-' in obj.name else
                  Vector((-1, 0, 0)) if '-side--1-' in obj.name else
                  Vector((1, 0, 0)) if '-side-1-' in obj.name else Vector((0, 1, 0)))
        tangent = Vector((normal.y, -normal.x, 0))
        points = [v.co for v in obj.data.vertices]
        center = sum(points, Vector()) / len(points)
        width = max(p.dot(tangent) for p in points) - min(p.dot(tangent) for p in points)
        height = max(p.z for p in points) - min(p.z for p in points)
        direction = (root.matrix_world.to_3x3() @ normal).normalized()
        for column in (-1, 0, 1):
            for row in (-1, 0, 1):
                local = center + tangent * width * column / 3 + Vector((0, 0, height * row / 3))
                origin = root.matrix_world @ local + direction * .035
                hit, _, index, distance = tree.ray_cast(origin, direction, .65)
                check = {'window': obj.name, 'pane': [column + 1, row + 1]}
                checks.append(check)
                if hit is not None:
                    failures.append({**check, 'obstruction': owners[index], 'distance': distance})
report = {'sourcePass': 68, 'windows': len(checks) // 9, 'paneRays': len(checks),
          'outwardDistance': .65, 'violations': failures}
if '--' in sys.argv:
    path = Path(sys.argv[sys.argv.index('--') + 1])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n')
assert checks, 'No source68 windows found'
assert not failures, json.dumps(failures[:12])
print('PASS', report['paneRays'], 'pane rays through', report['windows'], 'windows')
