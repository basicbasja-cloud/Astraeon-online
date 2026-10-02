"""Give the saved Consortium Hall a processional south entrance above its stairs."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
assert bpy.context.scene.get('world_id') == 'wayfarer-spatial'
owner = bpy.data.collections['guild-hall']
parent = bpy.data.objects['guild-hall-placement']
inverse = parent.matrix_world.inverted()
prefix = 'wayfarer-hall-front-'
for obj in list(owner.objects):
    if obj.name.startswith(prefix):
        bpy.data.objects.remove(obj, do_unlink=True)


def mesh(name, vertices, faces, material):
    data = bpy.data.meshes.new(prefix + name)
    data.from_pydata([inverse @ Vector(p) for p in vertices], [], faces)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    data.materials.append(bpy.data.materials[material])
    data.uv_layers.new(name='Hall-front-UV')
    for face in data.polygons:
        normal = face.normal
        axes = (0, 1) if abs(normal.z) > .6 else (0, 2) if abs(normal.y) > abs(normal.x) else (1, 2)
        for loop in face.loop_indices:
            point = data.vertices[data.loops[loop].vertex_index].co
            data.uv_layers.active.data[loop].uv = (point[axes[0]] / 2.4, point[axes[1]] / 2.4)
    obj = bpy.data.objects.new(prefix + name, data)
    owner.objects.link(obj)
    obj.parent = parent
    obj['role'] = 'decorative'
    obj['shadow'] = False
    return obj


def box(name, center, size, material):
    x, y, z = center
    dx, dy, dz = (v / 2 for v in size)
    vs = [(x + a * dx, y + b * dy, z + c * dz)
          for c in (-1, 1) for b in (-1, 1) for a in (-1, 1)]
    fs = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
          [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    return mesh(name, vs, fs, material)


def beam(name, start, end, radius, material, sides=6):
    a, b = Vector(start), Vector(end)
    axis = (b - a).normalized()
    u = axis.cross(Vector((0, 0, 1)))
    if u.length < .001:
        u = Vector((1, 0, 0))
    u.normalize()
    v = axis.cross(u).normalized()
    vs = [tuple(p + radius * (u * math.cos(i * math.tau / sides) +
                                    v * math.sin(i * math.tau / sides)))
          for p in (a, b) for i in range(sides)]
    fs = [list(reversed(range(sides))), list(range(sides, 2 * sides))]
    fs += [[i, (i+1) % sides, (i+1) % sides + sides, i+sides] for i in range(sides)]
    return mesh(name, vs, fs, material)


cx, front, back = 21.45, 14.23, 13.18
left, right = cx - 1.1, cx + 1.1
box('portal-core', (cx, (front + back)/2, 3.7), (2.2, front-back, 6.5), 'stoneLight')
mesh('portal-gable', [(left, front+.015, 6.95), (right, front+.015, 6.95),
                      (cx, front+.015, 8.45)], [[0, 1, 2]], 'cream')
for j, x0 in enumerate((left, right)):
    x1 = cx
    mesh(f'blue-roof-{j}', [(x0, back-.08, 6.95), (x0, front+.22, 6.95),
                           (x1, front+.22, 8.45), (x1, back-.08, 8.45)],
         [[0, 1, 2, 3]], 'slate')
    beam(f'roof-gold-rib-{j}', (x0, front+.245, 6.95), (cx, front+.245, 8.45), .045, 'gold')
beam('roof-ridge', (cx, back-.08, 8.49), (cx, front+.25, 8.49), .055, 'gold')
beam('roof-finial', (cx, front+.10, 8.45), (cx, front+.10, 9.15), .075, 'gold')

# A deep, legible entrance is centred on the existing public stair approach.
box('door-recess', (cx, front+.04, 1.78), (1.16, .045, 2.28), 'timber')
box('door-center', (cx, front+.075, 1.74), (.055, .055, 2.12), 'gold')
for side, x in enumerate((cx-.65, cx+.65)):
    box(f'door-jamb-{side}', (x, front+.10, 1.92), (.18, .19, 2.65), 'cream')
    beam(f'arch-{side}', (x, front+.13, 3.20), (cx, front+.13, 3.77), .09, 'gold')
    box(f'buttress-{side}', (x + (-.29 if side == 0 else .29), front+.17, 3.30),
        (.23, .31, 5.7), 'stoneLight')
    mesh(f'buttress-cap-{side}', [(x + (-.41 if side == 0 else .17), front+.17, 6.15),
                                 (x + (-.17 if side == 0 else .41), front+.17, 6.15),
                                 (x + (-.29 if side == 0 else .29), front+.17, 7.12)],
         [[0, 1, 2]], 'slate')

# Rose glass and eight-point ASTRAEON compass are read above the entry at play scale.
rose_z, rose_y = 5.34, front+.07
points = [(cx + math.cos(i*math.tau/16)*.54, rose_y,
           rose_z + math.sin(i*math.tau/16)*.54) for i in range(16)]
mesh('rose-glass', points, [list(range(16))], 'glass')
for i in range(16):
    beam(f'rose-ring-{i}', points[i], points[(i+1)%16], .045, 'gold')
for i in range(8):
    a = math.pi/2 + i*math.tau/8
    beam(f'compass-ray-{i}', (cx, rose_y+.025, rose_z),
         (cx + math.cos(a)*.39, rose_y+.025, rose_z + math.sin(a)*.39), .028, 'gold')
box('rose-core', (cx, rose_y+.035, rose_z), (.14, .05, .14), 'gold')

for side, x in enumerate((cx-1.48, cx+1.48)):
    mesh(f'heraldic-banner-{side}', [(x-.22, front+.03, 2.75),
                                    (x+.22, front+.03, 2.75),
                                    (x+.22, front+.03, 4.57),
                                    (x-.22, front+.03, 4.57)], [[0, 1, 2, 3]], 'clothBlue')
    for i in range(4):
        a = math.pi/2 + i*math.pi/2
        beam(f'banner-star-{side}-{i}', (x, front+.055, 3.72),
             (x+math.cos(a)*.15, front+.055, 3.72+math.sin(a)*.15), .025, 'gold')

bpy.context.view_layer.update()
target = ROOT / 'authoring/wayfarer-spatial.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print('Saved south-facing Consortium Hall facade:', target)
