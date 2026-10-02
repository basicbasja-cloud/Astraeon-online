"""Finish the existing West Gate pennants with ASTRAEON compass heraldry."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
assert bpy.context.scene.get("world_id") == "wayfarer-spatial"

OWNER = "caravan-gate"
COLLECTION = bpy.data.collections[OWNER]
PARENT = bpy.data.objects[OWNER + "-placement"]
INVERSE = PARENT.matrix_world.inverted()
PREFIX = "wayfarer-gate-heraldry-"

for obj in list(COLLECTION.objects):
    if obj.name.startswith(PREFIX):
        bpy.data.objects.remove(obj, do_unlink=True)
for data in list(bpy.data.meshes):
    if data.name.startswith(PREFIX) and data.users == 0:
        bpy.data.meshes.remove(data)


def mesh(name, vertices, faces, material_name):
    data = bpy.data.meshes.new(name)
    data.from_pydata([INVERSE @ Vector(v) for v in vertices], [], faces)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    data.materials.append(bpy.data.materials[material_name])
    data.uv_layers.new(name="Wayfarer-gate-heraldry")
    for polygon in data.polygons:
        normal = polygon.normal
        axes = (0, 1) if abs(normal.z) > 0.6 else (0, 2) if abs(normal.y) > abs(normal.x) else (1, 2)
        for loop in polygon.loop_indices:
            point = data.vertices[data.loops[loop].vertex_index].co
            data.uv_layers.active.data[loop].uv = (point[axes[0]] / 2.4, point[axes[1]] / 2.4)
    obj = bpy.data.objects.new(name, data)
    COLLECTION.objects.link(obj)
    obj.parent = PARENT
    obj["role"] = "decorative"
    obj["shadow"] = False
    obj["frontage_iteration"] = True
    return obj


def beam(name, start, end, radius, material_name):
    start, end = Vector(start), Vector(end)
    axis = (end - start).normalized()
    u = axis.cross(Vector((0, 0, 1)))
    if u.length < 0.01:
        u = Vector((1, 0, 0))
    u.normalize()
    v = axis.cross(u).normalized()
    sides = 6
    vertices = [
        tuple(point + radius * (u * math.cos(i * math.tau / sides) + v * math.sin(i * math.tau / sides)))
        for point in (start, end)
        for i in range(sides)
    ]
    faces = [list(reversed(range(sides))), list(range(sides, 2 * sides))]
    faces.extend([[i, (i + 1) % sides, (i + 1) % sides + sides, i + sides] for i in range(sides)])
    return mesh(name, vertices, faces, material_name)


def star(name, center, radius, material_name, points=8, inner_ratio=0.38):
    center = Vector(center)
    vertices = []
    for index in range(points * 2):
        angle = math.pi / 2 + index * math.tau / (points * 2)
        r = radius if index % 2 == 0 else radius * inner_ratio
        vertices.append((center.x + math.cos(angle) * r, center.y, center.z + math.sin(angle) * r))
    return mesh(name, vertices, [list(range(len(vertices)))], material_name)


for index in range(2):
    banner = bpy.data.objects[f"caravan-gate-banner-{index}"]
    corners = [banner.matrix_world @ Vector(corner) for corner in banner.bound_box]
    min_x, max_x = min(p.x for p in corners), max(p.x for p in corners)
    min_z, max_z = min(p.z for p in corners), max(p.z for p in corners)
    front_y = max(p.y for p in corners) + 0.038
    inset = 0.055
    left, right = min_x + inset, max_x - inset
    top, bottom = max_z - 0.12, min_z + 0.12

    # Narrow stitched piping and a clipped lower hem frame the woven blue cloth.
    beam(f"{PREFIX}edge-left-{index}", (left, front_y, bottom), (left, front_y, top), 0.012, "gold")
    beam(f"{PREFIX}edge-right-{index}", (right, front_y, bottom), (right, front_y, top), 0.012, "gold")
    beam(f"{PREFIX}hem-top-{index}", (left, front_y, top), (right, front_y, top), 0.012, "gold")
    beam(f"{PREFIX}hem-bottom-{index}", (left, front_y, bottom), (right, front_y, bottom), 0.016, "gold")

    center = Vector(((min_x + max_x) / 2, front_y + 0.01, min_z + (max_z - min_z) * 0.53))
    star(f"{PREFIX}compass-{index}", center, (max_x - min_x) * 0.39, "gold", points=8)
    star(f"{PREFIX}compass-core-{index}", (center.x, center.y + 0.012, center.z), (max_x - min_x) * 0.10, "teal", points=4, inner_ratio=0.12)

bpy.context.view_layer.update()
target = ROOT / "authoring/wayfarer-spatial.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print("Saved compass heraldry to the existing West Gate pennants:", target)
