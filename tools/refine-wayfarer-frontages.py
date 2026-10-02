"""Refine functional frontages in the saved Wayfarer scene, without rebuilding it.

This is a local Golden iteration, not the deferred production kit extraction.
Existing meshes/IDs remain editable; replaced details stay as hidden references.
Run with the current authoring/wayfarer-spatial.blend open.
"""
import json
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
assert bpy.context.scene['world_id'] == 'wayfarer-spatial'
bpy.context.view_layer.update()


def material(name, color):
    result = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    return result


material('forgeEmber', (.98, .42, .08))
material('forgeHotCore', (1, .78, .28))
material('shrineAzure', (.28, .60, .70))


def mesh(owner, name, vertices, faces, mat, role='decorative', shadow=True):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    collection = bpy.data.collections[owner]
    parent = bpy.data.objects[owner + '-placement']
    inverse = parent.matrix_world.inverted()
    data = bpy.data.meshes.new(name)
    data.from_pydata([inverse @ Vector(v) for v in vertices], [], faces)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    data.materials.append(bpy.data.materials[mat])
    data.uv_layers.new(name='Wayfarer-painterly')
    for polygon in data.polygons:
        normal = polygon.normal
        axes = (0, 1) if abs(normal.z) > .6 else (0, 2) if abs(normal.y) > abs(normal.x) else (1, 2)
        for loop in polygon.loop_indices:
            point = data.vertices[data.loops[loop].vertex_index].co
            data.uv_layers.active.data[loop].uv = (point[axes[0]] / 2.4, point[axes[1]] / 2.4)
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.parent = parent
    obj['role'] = role
    obj['shadow'] = shadow
    obj['frontage_iteration'] = True
    return obj


def box(owner, name, center, size, mat, role='decorative', shadow=True):
    p = Vector(center)
    a, b, h = [v / 2 for v in size]
    vs = [tuple(p + Vector((x * a, y * b, z * h))) for z in [-1, 1] for y in [-1, 1] for x in [-1, 1]]
    return mesh(owner, name, vs, [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5]], mat, role, shadow)


def beam(owner, name, a, b, radius, mat, shadow=True):
    a, b = Vector(a), Vector(b)
    axis = (b - a).normalized()
    u = axis.cross(Vector((0, 0, 1)))
    if u.length < .01:
        u = Vector((1, 0, 0))
    u.normalize()
    v = axis.cross(u).normalized()
    n = 6
    vs = [tuple(p + radius * (u * math.cos(j * math.tau / n) + v * math.sin(j * math.tau / n))) for p in [a, b] for j in range(n)]
    fs = [list(range(n - 1, -1, -1)), list(range(n, n * 2))] + [[j, (j + 1) % n, (j + 1) % n + n, j + n] for j in range(n)]
    return mesh(owner, name, vs, fs, mat, shadow=shadow)


def retain_reference(name):
    obj = bpy.data.objects[name]
    obj['render_visible'] = False
    obj.hide_render = True
    obj.hide_set(True)


def world_center(name):
    obj = bpy.data.objects[name]
    return sum((obj.matrix_world @ v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)


# Bronze Anvil: a real open fire chamber, masonry hood, stock and tool rack.
# The earlier detached flame triangles are retained as editing references.
owner = 'artisan-workshop'
hearth = world_center('artisan-workshop-forge-hearth')
x, y = hearth.x, hearth.y
for j in range(3):
    retain_reference(f'forge-hearth-flame-{j}')
box(owner, 'forge-chamber-back', (x, y - .25, .72), (1.05, .18, 1.44), 'stone', 'solid')
for j, side in enumerate([-1, 1]):
    box(owner, f'forge-chamber-jamb-{j}', (x + side * .43, y, .72), (.20, .56, 1.44), 'stone', 'solid')
box(owner, 'forge-chamber-lintel', (x, y, 1.39), (1.12, .64, .24), 'iron')
box(owner, 'forge-chamber-dark-recess', (x, y + .05, .83), (.62, .015, .68), 'iron', shadow=False)
mesh(owner, 'forge-tapered-hood', [(x + sx * a, y + sy * b, z) for z, a, b in [(1.5, .62, .38), (2.14, .28, .20)] for sy in [-1, 1] for sx in [-1, 1]], [[0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5], [4, 5, 7, 6]], 'iron')
# Embers are authored geometry, with no dynamic light/shadow renderer cost.
for j in range(7):
    qx = x + ((j % 4) - 1.5) * .13
    qy = y + .14 + (j // 4) * .10
    box(owner, f'forge-ember-bed-{j}', (qx, qy, .80), (.12, .13, .055), 'forgeEmber', shadow=False)
    mesh(owner, f'forge-grounded-flame-{j}', [(qx - .065, qy, .82), (qx + .065, qy, .82), (qx + .025, qy, 1.02 + (j % 3) * .075)], [[0, 1, 2]], 'forgeHotCore', shadow=False)
beam(owner, 'forge-hood-flue', (x, y - .05, 2.14), (x, y - .32, 2.65), .13, 'iron')
# Rack stays on the existing workshop side wall, leaving the public avenue clear.
body = bpy.data.objects[owner + '-walls']
points = [body.matrix_world @ v.co for v in body.data.vertices[:4]]
a, b = points[2], points[3]
tangent = (b - a).normalized()
outward = Vector((-tangent.y, tangent.x, 0)) * .08
for j, fraction in enumerate([.25, .46, .67]):
    p = a.lerp(b, fraction) + outward
    beam(owner, f'forge-tool-handle-{j}', tuple(p + Vector((0, 0, .8))), tuple(p + Vector((0, 0, 1.65))), .025, 'oak')
    beam(owner, f'forge-tool-head-{j}', tuple(p - tangent * .14 + Vector((0, 0, 1.65))), tuple(p + tangent * .14 + Vector((0, 0, 1.65))), .065, 'iron')
beam(owner, 'forge-tool-rack', tuple(a.lerp(b, .15) + outward + Vector((0, 0, 1.5))), tuple(a.lerp(b, .78) + outward + Vector((0, 0, 1.5))), .055, 'timber')

# Luna Shrine: align the ceremonial approach with the existing southern door.
# The eastern chapel/portal remains; the main processional entrance is distinct.
owner = 'moon-shrine'
door = world_center('moon-shrine-door')
wall = bpy.data.objects['moon-shrine-walls']
points = [wall.matrix_world @ v.co for v in wall.data.vertices[:4]]
tangent = (points[3] - points[0]).normalized()
outward = Vector((-tangent.y, tangent.x, 0))
front = Vector((door.x, door.y, 0)) + outward * .08
up = Vector((0, 0, 1))
for name in ['shrine-buttress-3-1', 'shrine-lancet-3-1', 'shrine-jamb-3-1--1', 'shrine-jamb-3-1-1']:
    retain_reference(name)
for j, side in enumerate([-1, 1]):
    p = front + tangent * .48 * side
    beam(owner, f'shrine-main-door-jamb-{j}', tuple(p + up * .22), tuple(p + up * 1.84), .08, 'stoneLight')
    beam(owner, f'shrine-main-pointed-arch-{j}', tuple(p + up * 1.84), tuple(front + up * 2.65), .075, 'gold')
    beam(owner, f'shrine-main-outer-arch-{j}', tuple(p + tangent * .12 * side + up * 1.84), tuple(front + up * 2.82), .055, 'stoneLight')
beam(owner, 'shrine-main-door-split', tuple(front + up * .24), tuple(front + up * 1.79), .022, 'gold')
# Azure moon glass and celestial tracery replace a blank domestic frontage.
center = front + up * 3.7
n = 24
mesh(owner, 'shrine-main-moon-glass', [tuple(center)] + [tuple(center + tangent * math.cos(j * math.tau / n) * .43 + up * math.sin(j * math.tau / n) * .43) for j in range(n)], [[0, j + 1, (j + 1) % n + 1] for j in range(n)], 'shrineAzure', shadow=False)
for j in range(n):
    angle, next_angle = j * math.tau / n, (j + 1) * math.tau / n
    a = center + tangent * math.cos(angle) * .46 + up * math.sin(angle) * .46 + outward * .015
    b = center + tangent * math.cos(next_angle) * .46 + up * math.sin(next_angle) * .46 + outward * .015
    beam(owner, f'shrine-main-rose-rim-{j}', tuple(a), tuple(b), .028, 'gold', shadow=False)
for j in range(8):
    angle = j * math.tau / 8
    end = center + tangent * math.cos(angle) * .40 + up * math.sin(angle) * .40 + outward * .02
    beam(owner, f'shrine-main-rose-ray-{j}', tuple(center + outward * .02), tuple(end), .016, 'gold', shadow=False)
# An actual bell silhouette and open-looking recess in the tower's visible face.
tower = bpy.data.objects['moon-shrine-bell-tower']
vs = [tower.matrix_world @ v.co for v in tower.data.vertices]
tx = sum(v.x for v in vs) / len(vs)
ty = max(v.y for v in vs) + .035
box(owner, 'shrine-bell-recess', (tx, ty, 6.22), (.46, .02, .78), 'glass', shadow=False)
beam(owner, 'shrine-bell-yoke', (tx - .21, ty + .035, 6.50), (tx + .21, ty + .035, 6.50), .035, 'gold')
mesh(owner, 'shrine-sanctuary-bell', [(tx + math.cos(j * math.tau / 8) * r, ty + .07 + math.sin(j * math.tau / 8) * r, z) for z, r in [(5.95, .17), (6.08, .12), (6.35, .08)] for j in range(8)], [[j + k * 8, (j + 1) % 8 + k * 8, (j + 1) % 8 + (k + 1) * 8, j + (k + 1) * 8] for k in range(2) for j in range(8)], 'gold')
beam(owner, 'shrine-bell-clapper', (tx, ty + .07, 6.12), (tx, ty + .07, 5.88), .022, 'iron')
# Move the saved stair/landing surfaces together once; metadata and geometry
# derive their new centre from the actual door, not replacement runtime values.
root = bpy.data.objects[owner + '-placement']
if not root.get('main_approach_aligned'):
    step = world_center('shrine-step-1')
    delta = Vector((door.x - step.x, 0, 0))
    for name in ['shrine-step-0', 'shrine-step-1', 'shrine-step-2', 'shrine-stair-navigation', 'shrine-landing-navigation']:
        obj = bpy.data.objects[name]
        matrix = obj.matrix_world.copy()
        matrix.translation += delta
        obj.matrix_world = matrix
    for name, distance in [('moon-shrine-entrance', .85), ('moon-shrine-approach', 1.55)]:
        obj = bpy.data.objects.get(name)
        if obj:
            matrix = obj.matrix_world.copy()
            matrix.translation.x = door.x
            matrix.translation.y = door.y + distance
            obj.matrix_world = matrix
    root['main_approach_aligned'] = True

# Grounding follows real tread tops, instead of putting feet below a visible
# step while following the old continuous ramp. Navigation stays lightweight:
# seven authored rectangles, not mesh physics. Keep the ramp meshes as source
# references, but exclude them from runtime walkable/elevation surfaces.
terrain = bpy.data.collections['court-terrain']
for owner, prefix, count, ramp in [('moon-shrine', 'shrine-step-', 3, 'shrine-stair-navigation'), ('guild-hall', 'civic-processional-step-', 4, 'civic-stair-navigation')]:
    bpy.data.objects[ramp]['walkable'] = False
    parent = bpy.data.objects[owner + '-placement']
    for j in range(count):
        original = bpy.data.objects[prefix + str(j)]
        world = original.matrix_world.copy()
        original.parent = parent
        original.matrix_world = world
        vs = [original.matrix_world @ vertex.co for vertex in original.data.vertices]
        top = max(vertex.z for vertex in vs)
        points = [vertex for vertex in vs if abs(vertex.z - top) < .0001]
        center = sum(points, Vector()) / len(points)
        points.sort(key=lambda vertex: math.atan2(vertex.y - center.y, vertex.x - center.x))
        obj = mesh(owner, prefix + str(j) + '-contact-surface', [tuple(vertex) for vertex in points], [list(range(len(points)))], 'paving', shadow=False)
        for collection in list(obj.users_collection):
            if collection != terrain:
                collection.objects.unlink(obj)
        if obj.name not in terrain.objects:
            terrain.objects.link(obj)
        obj['surface_role'] = 'forecourt'
        obj['object_id'] = owner
        obj['walkable'] = True
        obj['render_visible'] = False
        obj['tread_source'] = original.name

# Source-owned portal height agrees with the actual tread below it.
portal = bpy.data.objects['moon-shrine-entrance']
world = portal.matrix_world.copy()
for j in range(3):
    step = bpy.data.objects[f'shrine-step-{j}']
    vs = [step.matrix_world @ vertex.co for vertex in step.data.vertices]
    if min(v.x for v in vs) <= world.translation.x <= max(v.x for v in vs) and min(v.y for v in vs) <= world.translation.y <= max(v.y for v in vs):
        world.translation.z = max(v.z for v in vs)
portal.matrix_world = world

# The Seafarer's Rest: a hanging maritime sign readable as a social destination.
owner = 'east-inn'
front = world_center('east-inn-door')
sign = Vector((front.x - .73, front.y + .42, 2.4))
beam(owner, 'inn-sign-bracket', (sign.x, sign.y - .48, 2.95), (sign.x, sign.y + .08, 2.95), .05, 'iron')
for j, dx in enumerate([-.16, .16]):
    beam(owner, f'inn-sign-chain-{j}', (sign.x + dx, sign.y, 2.95), (sign.x + dx, sign.y, 2.63), .013, 'iron')
box(owner, 'inn-traveler-sign', tuple(sign), (.59, .08, .48), 'slate')
beam(owner, 'inn-sign-mast', (sign.x, sign.y + .05, 2.25), (sign.x, sign.y + .05, 2.56), .018, 'gold', shadow=False)
mesh(owner, 'inn-sign-sail', [(sign.x + .035, sign.y + .06, 2.55), (sign.x + .20, sign.y + .06, 2.30), (sign.x + .035, sign.y + .06, 2.30)], [[0, 1, 2]], 'cream', shadow=False)
beam(owner, 'inn-sign-hull', (sign.x - .18, sign.y + .06, 2.26), (sign.x + .19, sign.y + .06, 2.26), .025, 'gold', shadow=False)

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'))
runpy.run_path(str(ROOT / 'tools/export-world-v3.py'), run_name='__main__')
print('Saved working forge, ceremonial shrine approach and maritime inn frontage; original scene retained')
