"""Give the existing interactive Quest Board authored, readable postings."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
assert bpy.context.scene.get("world_id") == "wayfarer-spatial"

OWNER = "guild-board"
COLLECTION = bpy.data.collections[OWNER]
PARENT = bpy.data.objects[OWNER + "-placement"]
INVERSE = PARENT.matrix_world.inverted()

# Replace only this iteration's detail meshes when the script is rerun.
for obj in list(COLLECTION.objects):
    if obj.name.startswith("quest-board-detail-"):
        bpy.data.objects.remove(obj, do_unlink=True)
for data in list(bpy.data.meshes):
    if data.name.startswith("quest-board-detail-") and data.users == 0:
        bpy.data.meshes.remove(data)

parchment = bpy.data.materials.get("questParchment") or bpy.data.materials.new("questParchment")
parchment.diffuse_color = (0.88, 0.75, 0.53, 1.0)


def mesh(name, vertices, faces, material_name):
    data = bpy.data.meshes.new(name)
    data.from_pydata([INVERSE @ Vector(v) for v in vertices], [], faces)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    data.materials.append(bpy.data.materials[material_name])
    data.uv_layers.new(name="Wayfarer-painted-notice")
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


def box(name, center, size, material_name):
    p = Vector(center)
    sx, sy, sz = [v / 2 for v in size]
    vertices = [tuple(p + Vector((x * sx, y * sy, z * sz))) for z in (-1, 1) for y in (-1, 1) for x in (-1, 1)]
    return mesh(name, vertices, [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5]], material_name)


def line(name, start, end, radius, material_name):
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


def marker(name, center_x, center_y, center_z, radius, material_name, star=False):
    vertices = []
    for i in range(16 if star else 10):
        angle = math.pi / 2 + i * math.tau / (16 if star else 10)
        scale = radius if not star or i % 2 == 0 else radius * 0.36
        vertices.append((center_x + math.cos(angle) * scale, center_y, center_z + math.sin(angle) * scale))
    return mesh(name, vertices, [list(range(len(vertices)))], material_name)


# The service prop is small in the gameplay view. Three distinct paper slips,
# clear ink strokes and colored tacks make it read as an in-world quest board.
paper_centers = [23.56, 23.80, 24.04]
paper_styles = [("gold", 0.36), ("terracotta", 0.26), ("teal", 0.36)]
for side, y in (("front", 15.105), ("back", 14.918)):
    for index, (center_x, (seal_material, variation)) in enumerate(zip(paper_centers, paper_styles)):
        width, height = 0.19, 0.49
        bottom = 1.36 + (0.015 if index == 1 else 0)
        top = bottom + height
        curl = 0.025 if index == 2 else 0.0
        vertices = [
            (center_x - width / 2, y, top),
            (center_x + width / 2, y, top),
            (center_x + width / 2, y, bottom + curl),
            (center_x, y, bottom),
            (center_x - width / 2, y, bottom + curl),
        ]
        mesh(f"quest-board-detail-paper-{index}-{side}", vertices, [[0, 1, 2, 3, 4]], "questParchment")
        mark_y = y + (0.009 if side == "front" else -0.009)
        marker(
            f"quest-board-detail-seal-{index}-{side}",
            center_x,
            mark_y,
            top - 0.075,
            0.035,
            seal_material,
            star=index == 0,
        )
        # Handwritten rules are stylized as short, varied ink strokes.
        for row in range(3):
            z = top - 0.18 - row * 0.085
            length = 0.105 if (row + index) % 2 else 0.125
            if row == 2 and index == 1:
                length = 0.072
            ink_y = mark_y + (0.006 if side == "front" else -0.006)
            line(
                f"quest-board-detail-ink-{index}-{row}-{side}",
                (center_x - length / 2, ink_y, z),
                (center_x + length / 2, ink_y, z),
                0.0045,
                "timber",
            )

    # A small blue title rail and gold compass seal brand the posting board.
    box(f"quest-board-detail-header-{side}", (23.8, y, 1.965), (0.70, 0.028, 0.105), "clothBlue")
    marker(
        f"quest-board-detail-header-star-{side}",
        23.8,
        y + (0.018 if side == "front" else -0.018),
        1.965,
        0.038,
        "gold",
        star=True,
    )

bpy.context.view_layer.update()
target = ROOT / "authoring/wayfarer-spatial.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print("Saved authored postings on the existing Quest Board to", target)
