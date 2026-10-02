"""Author a small Lantern Market threshold in the existing Wayfarer scene.

The gateway marks the market mouth with ASTRAEON's blue-and-gold compass
language while leaving the street opening clear. It is an authored scene edit,
not a town rebuild.
"""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
assert bpy.context.scene.get("world_id") == "wayfarer-spatial"

OWNER = "market-shop"
COLLECTION = bpy.data.collections[OWNER]
PARENT = bpy.data.objects[OWNER + "-placement"]
INVERSE = PARENT.matrix_world.inverted()

# Rebuild only this named scene detail so the saved script remains repeatable.
for obj in list(COLLECTION.objects):
    if obj.name.startswith("market-gateway-"):
        bpy.data.objects.remove(obj, do_unlink=True)
for data in list(bpy.data.meshes):
    if data.name.startswith("market-gateway-") and data.users == 0:
        bpy.data.meshes.remove(data)

amber = bpy.data.materials.get("marketAmber") or bpy.data.materials.new("marketAmber")
amber.diffuse_color = (1.0, 0.62, 0.24, 1.0)


def mesh(name, vertices, faces, material_name):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    data = bpy.data.meshes.new(name)
    data.from_pydata([INVERSE @ Vector(v) for v in vertices], [], faces)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    data.materials.append(bpy.data.materials[material_name])
    data.uv_layers.new(name="Wayfarer-market-painterly")
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


def oriented_box(name, center, across, along, size, material_name):
    center = Vector(center)
    across = Vector(across).normalized()
    along = Vector(along).normalized()
    width, depth, height = size
    vertices = [
        tuple(center + across * (sx * width / 2) + along * (sy * depth / 2) + Vector((0, 0, sz * height / 2)))
        for sz in (-1, 1)
        for sy in (-1, 1)
        for sx in (-1, 1)
    ]
    return mesh(name, vertices, [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5]], material_name)


def beam(name, start, end, radius, material_name):
    start, end = Vector(start), Vector(end)
    axis = (end - start).normalized()
    u = axis.cross(Vector((0, 0, 1)))
    if u.length < 0.01:
        u = Vector((1, 0, 0))
    u.normalize()
    v = axis.cross(u).normalized()
    sides = 8
    vertices = [
        tuple(point + radius * (u * math.cos(i * math.tau / sides) + v * math.sin(i * math.tau / sides)))
        for point in (start, end)
        for i in range(sides)
    ]
    faces = [list(reversed(range(sides))), list(range(sides, 2 * sides))]
    faces.extend([[i, (i + 1) % sides, (i + 1) % sides + sides, i + sides] for i in range(sides)])
    return mesh(name, vertices, faces, material_name)


def compass_star(name, center, across, normal, radius):
    center = Vector(center)
    across = Vector(across).normalized()
    vertices = []
    for index in range(16):
        angle = math.pi / 2 + index * math.tau / 16
        r = radius if index % 2 == 0 else radius * 0.38
        vertices.append(tuple(center + across * (math.cos(angle) * r) + Vector((0, 0, math.sin(angle) * r)) + Vector(normal) * 0.018))
    return mesh(name, vertices, [list(range(16))], "gold")


# The first authored street segment runs from (25.8, 21.5) toward (30, 22.5).
# Move the marker .8 m into that lane, beyond the fountain's visual edge. Its
# 2.3 m clear opening leaves ample room for the normal actor path.
street_center = Vector((26.58, 21.68, 0))
direction = Vector((4.2, 1.0, 0)).normalized()
across = Vector((-direction.y, direction.x, 0)).normalized()
normal = direction
post_points = [street_center + across * 1.16, street_center - across * 1.16]

for index, point in enumerate(post_points):
    oriented_box(f"market-gateway-foot-{index}", point + Vector((0, 0, 0.14)), (1, 0, 0), (0, 1, 0), (0.28, 0.28, 0.28), "stone")
    beam(f"market-gateway-post-{index}", point + Vector((0, 0, 0.27)), point + Vector((0, 0, 3.38)), 0.06, "timber")
    oriented_box(f"market-gateway-band-low-{index}", point + Vector((0, 0, 0.62)), across, normal, (0.15, 0.15, 0.06), "gold")
    oriented_box(f"market-gateway-band-high-{index}", point + Vector((0, 0, 3.08)), across, normal, (0.15, 0.15, 0.06), "gold")
    beam(f"market-gateway-cap-{index}", point + Vector((0, 0, 3.34)), point + Vector((0, 0, 3.60)), 0.10, "gold")

beam("market-gateway-lintel", post_points[0] + Vector((0, 0, 3.48)), post_points[1] + Vector((0, 0, 3.48)), 0.075, "timber")

# Folded blue cloth, stitched in gold, hangs in the street's approach plane.
banner_center = street_center + normal * 0.035
left_top = banner_center - across * 0.49 + Vector((0, 0, 3.30))
right_top = banner_center + across * 0.49 + Vector((0, 0, 3.30))
right_bottom = banner_center + across * 0.49 + Vector((0, 0, 2.56))
bottom_point = banner_center + Vector((0, 0, 2.40))
left_bottom = banner_center - across * 0.49 + Vector((0, 0, 2.56))
mesh(
    "market-gateway-compass-banner",
    [tuple(v) for v in (left_top, right_top, right_bottom, bottom_point, left_bottom)],
    [[0, 1, 2, 3, 4]],
    "clothBlue",
)
beam("market-gateway-banner-stitch-left", left_top, left_bottom, 0.014, "gold")
beam("market-gateway-banner-stitch-right", right_top, right_bottom, 0.014, "gold")
compass_star("market-gateway-star", banner_center + Vector((0, 0, 2.94)), across, normal, 0.22)

# Warm lantern boxes hang beside the pennant, with compact, decorative frames.
for index, side in enumerate((-1, 1)):
    across_offset = across * (side * 0.78)
    center = street_center + across_offset + Vector((0, 0, 3.16))
    bracket_start = street_center + across_offset + Vector((0, 0, 3.43))
    bracket_end = street_center + across_offset + normal * 0.18 + Vector((0, 0, 3.43))
    beam(f"market-gateway-lantern-hanger-{index}", bracket_start, bracket_end, 0.028, "timber")
    oriented_box(f"market-gateway-lantern-frame-{index}", center, across, normal, (0.27, 0.25, 0.36), "gold")
    oriented_box(
        f"market-gateway-lantern-glass-{index}",
        center + normal * 0.012,
        across,
        normal,
        (0.17, 0.16, 0.23),
        "marketAmber",
    )
    oriented_box(
        f"market-gateway-lantern-crown-{index}",
        center + Vector((0, 0, 0.20)),
        across,
        normal,
        (0.32, 0.30, 0.07),
        "timber",
    )
    oriented_box(
        f"market-gateway-lantern-foot-{index}",
        center - Vector((0, 0, 0.20)),
        across,
        normal,
        (0.30, 0.28, 0.07),
        "timber",
    )

bpy.context.view_layer.update()
target = ROOT / "authoring/wayfarer-spatial.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print("Saved Lantern Market gateway to", target)
