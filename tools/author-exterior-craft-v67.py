"""Finish saved-town roof edges, entrance joinery and side-wall framing.

Run on saved source65. Original lots, walls, floors, anchors and collision stay
in place. This pass replaces only its own meshes and changes material/UV/light
authoring; corner and ground lighting must be baked after the saved export.
"""
import json
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('layout_id') == 'wayfarer-concept-terraced-town-v49'
assert scene.get('frontage_family_version') == 65
PREFIX = 'exterior-v67-'
for obj in list(bpy.data.objects):
    if obj.name.startswith(PREFIX):
        bpy.data.objects.remove(obj, do_unlink=True)
for data in list(bpy.data.meshes):
    if data.name.startswith(PREFIX) and not data.users:
        bpy.data.meshes.remove(data)

atlas = json.loads((ROOT / 'authoring/materials/wayfarer-exteriors-v67.json').read_text())
for material in bpy.data.materials:
    name = material.name.lower()
    tile = (0 if any(s in name for s in ('terracotta', 'roofclay')) else
            1 if any(s in name for s in ('slate', 'roofblue', 'roofmoss')) else
            2 if name in ('wood', 'oak', 'timber', 'civicdoor') else
            3 if name in ('stone', 'stonelight', 'cream', 'wallstone', 'wallcap',
                         'civicivory', 'civicshadow', 'streetivory') else None)
    if tile is None:
        continue
    previous = json.loads(material.get('texture_json', '{}'))
    material['texture_json'] = json.dumps({
        'file': atlas['asset'], 'grid': [2, 2], 'tile': tile,
        'worldSize': previous.get('worldSize', 3.2 if tile < 2 else 2.4),
        'meanLinearRGB': atlas['tiles'][tile]['meanLinearRGB'],
        'paletteDetail': [0.82, 0.78, 0.64, 0.68][tile],
    })

owner = root = None


def mesh(name, points, faces, material, shadow=True):
    data = bpy.data.meshes.new(PREFIX + name)
    data.from_pydata(points, [], faces)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(data)
    bm.free()
    data.materials.append(bpy.data.materials[material])
    data.uv_layers.new(name='PhysicalUV')
    size = json.loads(bpy.data.materials[material].get('texture_json', '{}')).get('worldSize', 2.4)
    for face in data.polygons:
        for li in face.loop_indices:
            p = data.vertices[data.loops[li].vertex_index].co
            n = face.normal
            # Timber grain runs along posts rather than across their height.
            data.uv_layers.active.data[li].uv = ((p.x / size, p.y / size)
                if abs(n.z) > .65 else (p.y / size, p.z / size)
                if abs(n.x) > abs(n.y) else (p.x / size, p.z / size))
    obj = bpy.data.objects.new(PREFIX + name, data)
    owner.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj['role'] = 'decorative'
    obj['shadow'] = shadow
    return obj


def box(name, center, size, material, shadow=True):
    x, y, z = center
    a, b, h = [v / 2 for v in size]
    return mesh(name, [(x + i * a, y + j * b, z + k * h)
                      for k in (-1, 1) for j in (-1, 1) for i in (-1, 1)],
                [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
                 [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]], material, shadow)


def beam(name, a, b, width, material='timber'):
    a, b = Vector(a), Vector(b)
    direction = (b - a).normalized()
    u = direction.cross(Vector((0, 1, 0)))
    if u.length < .01:
        u = direction.cross(Vector((1, 0, 0)))
    u.normalize()
    v = direction.cross(u).normalized()
    obj = mesh(name, [tuple(p + i * u * width / 2 + j * v * width / 2)
                     for p in (a, b) for i, j in [(-1, -1), (1, -1), (1, 1), (-1, 1)]],
               [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
                [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], material)
    # Each beam owns a longitudinal grain coordinate, including diagonal braces.
    size = json.loads(bpy.data.materials[material].get('texture_json', '{}')).get('worldSize', 2.4)
    for face in obj.data.polygons:
        for li in face.loop_indices:
            p = obj.data.vertices[obj.data.loops[li].vertex_index].co - a
            obj.data.uv_layers.active.data[li].uv = (p.dot(u) / size, p.dot(direction) / size)
    return obj


def local_points(obj):
    matrix = root.matrix_world.inverted() @ obj.matrix_world
    return [matrix @ v.co for v in obj.data.vertices]


records = []
roof_uvs = 0
frontage_indices = {name: i for i, name in enumerate(sorted(
    c.name for c in bpy.data.collections if c.name.startswith('frontage-')))}
for collection in sorted(bpy.data.collections, key=lambda c: c.name):
    placement = bpy.data.objects.get(collection.name + '-placement')
    if not placement or collection.get('family') not in ('residential', 'market', 'workshop', 'inn'):
        continue
    owner, root = collection, placement
    visible = [o for o in collection.objects if o.type == 'MESH' and o.get('render_visible', True)]
    walls = next((o for o in collection.objects if o.name.endswith('-walls')), None)
    if not walls:
        continue
    pts = local_points(walls)
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    base, h = min(p.z for p in pts), max(p.z for p in pts)
    if x1 - x0 < 2 or y1 - y0 < 2:
        continue
    frontal = collection.name.startswith('frontage-')
    roofs = [o for o in visible if '-curved-roof-' in o.name]
    profile = sorted({(round(p.x, 5), round(p.z, 5)) for o in roofs for p in local_points(o)})
    cumulative = [0.0]
    for (a, za), (b, zb) in zip(profile, profile[1:]):
        cumulative.append(cumulative[-1] + math.hypot(b - a, zb - za))
    crest = max(range(len(profile)), key=lambda i: profile[i][1]) if profile else None

    def arc_at(x):
        for i, ((a, za), (b, zb)) in enumerate(zip(profile, profile[1:])):
            if a - 1e-4 <= x <= b + 1e-4 and b > a:
                return cumulative[i] + max(0, min(1, (x - a) / (b - a))) * (cumulative[i + 1] - cumulative[i])
        raise ValueError(('roof profile', collection.name, x))

    # Tile U follows the ridge. V follows true curved-slope distance and shares
    # the same phase on adjacent strips, including the cut source65 dormer roof.
    for obj in visible:
        material = obj.data.materials[0]
        spec = json.loads(material.get('texture_json', '{}'))
        if spec.get('file') != atlas['asset'] or spec.get('tile') not in (0, 1):
            continue
        points = local_points(obj)
        if not obj.data.uv_layers.active:
            obj.data.uv_layers.new(name='PhysicalUV')
        if not obj.get('exterior_v67_original_uvs_json'):
            obj['exterior_v67_original_uvs_json'] = json.dumps([
                [list(obj.data.uv_layers.active.data[li].uv) for li in f.loop_indices]
                for f in obj.data.polygons])
        size = spec['worldSize']
        for face in obj.data.polygons:
            polygon = [points[i] for i in face.vertices]
            normal = (polygon[1] - polygon[0]).cross(polygon[2] - polygon[0]).normalized()
            if abs(normal.z) < .20:
                continue
            if normal.z < 0:
                normal.negate()
            ridge = Vector((-normal.y, normal.x, 0))
            if ridge.length < .01:
                continue
            ridge.normalize()
            if ridge[max(range(2), key=lambda i: abs(ridge[i]))] < 0:
                ridge.negate()
            upslope = normal.cross(ridge).normalized()
            if upslope.z < 0:
                upslope.negate()
            top = max(p.dot(upslope) for p in polygon)
            for li in face.loop_indices:
                p = points[obj.data.loops[li].vertex_index]
                uv = ((p.y / size, -(abs(arc_at(p.x) - cumulative[crest])) / size)
                      if obj in roofs else (p.dot(ridge) / size, (p.dot(upslope) - top) / size))
                obj.data.uv_layers.active.data[li].uv = uv
            roof_uvs += 1

    if not frontal:
        # Belts follow the actual rotated wall polygon, never an axis-aligned
        # bounding box wrapped around a differently oriented original house.
        top_face = next((f for f in walls.data.polygons
                         if all(abs(pts[i].z - h) < 1e-4 for i in f.vertices)), None)
        if not top_face:
            continue
        outline = [pts[i] for i in top_face.vertices]
        center = sum(outline, Vector()) / len(outline)
        levels = [(base + .24, .14, 'stoneLight'), (h - .12, .18, 'timber')]
        if h - base > 3.8:
            levels.append((base + (h - base) * .54, .14, 'oak'))
        for i, (a, b) in enumerate(zip(outline, outline[1:] + outline[:1])):
            outward = ((a + b) / 2 - center)
            outward.z = 0
            outward.normalize()
            for z, width, material in levels:
                aa, bb = a + outward * .07, b + outward * .07
                aa.z = bb.z = z
                beam(collection.name + '-belt-' + str((i, z)), aa, bb, width, material)
            corner = a + outward * .07
            beam(collection.name + '-post-bead-' + str(i),
                 (corner.x, corner.y, base + .25), (corner.x, corner.y, h - .24), .075, 'oak')
        records.append({'owner': collection.name, 'finish': 'wall-polygon belts and corner joinery'})
        continue

    x, y, w, d = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    floor = h * .53
    trim = 'oak' if collection.get('family') == 'residential' else 'timber'
    front = y1 + [.76, .89, .82][frontage_indices[collection.name] % 3]
    box(collection.name + '-jetty-cornice', (x, front + .20, floor + .13), (w + .40, .12, .075), 'oak')
    for side, xx in [(-1, x0), (1, x1)]:
        outer = xx + side * .20
        box(collection.name + '-side-eave-cornice', (outer, y, h - .09), (.12, d + .12, .13), trim)
        box(collection.name + '-side-midpost', (outer, y, (floor + h) / 2), (.12, .14, h - floor), trim)
        for yy in [y0 + d * .28, y0 + d * .72]:
            zz = h * .77
            box(collection.name + '-side-sill-' + str((side, yy)),
                (outer + side * .035, yy, zz - .72), (.32, 1.35, .12), 'stoneLight')
            for j in range(4):
                box(collection.name + '-shutter-louver-' + str((side, yy, j)),
                    (outer + side * .02, yy + .77, zz - .44 + j * .27), (.07, .26, .055), 'oak', False)
        for yy in (y0 + .20, y1 - .20):
            direction = 1 if yy < y else -1
            beam(collection.name + '-side-knee-' + str((side, yy)),
                 (outer, yy, h - .82), (outer, yy + direction * .56, h - .18), .105, trim)

    if roofs:
        roof_points = [p for o in roofs for p in local_points(o)]
        rx0, rx1 = min(p.x for p in roof_points), max(p.x for p in roof_points)
        ry0, ry1 = min(p.y for p in roof_points), max(p.y for p in roof_points)
        eave = min(p.z for p in roof_points)
        for side, xx in [(-1, rx0), (1, rx1)]:
            box(collection.name + '-eave-bead-' + str(side),
                (xx + side * .12, (ry0 + ry1) / 2, eave - .14), (.085, ry1 - ry0, .08), 'oak')
            count = max(4, round((ry1 - ry0) / .70))
            for j in range(count):
                yy = ry0 + (j + .5) * (ry1 - ry0) / count
                beam(collection.name + '-rafter-tail-' + str((side, j)),
                     (xx - side * .42, yy, eave - .32),
                     (xx + side * .12, yy, eave - .19), .12, trim)
        # Rounded ridge caps are separate original forms; the roof field itself
        # uses flat painted shingles. Preserve the existing ridge silhouette.
        for old in collection.objects:
            if old.name.startswith('attic-v62-') and '-ridge-crown' in old.name:
                old['render_visible'] = False
                old['shadow'] = False
        roofmat = roofs[0].data.materials[0].name
        peak_x, peak_z = profile[crest]
        cap_count = max(3, round((ry1 - ry0) / .85))
        for j in range(cap_count):
            ya = ry0 + j * (ry1 - ry0) / cap_count
            yb = ry0 + (j + 1) * (ry1 - ry0) / cap_count - .025
            arc = [(peak_x + math.cos(i * math.pi / 5) * .16,
                    peak_z + .035 + math.sin(i * math.pi / 5) * .16) for i in range(6)]
            obj = mesh(collection.name + '-ridge-cap-' + str(j),
                       [(xx, yy, zz) for yy in (ya, yb) for xx, zz in arc],
                       [[i, i + 1, i + 7, i + 6] for i in range(5)] +
                       [list(range(5, -1, -1)), list(range(6, 12))], roofmat)
            obj['role'] = 'overhead'

    # Replace the old flat rectangular door and segmented timber arch with an
    # arched timber leaf, deeper dressed-stone surround and visible ironwork.
    for old in collection.objects:
        if (old.name.startswith('plan-v44-') and old.name.endswith('-door')) or (
                old.name.startswith('organic-v47-') and any(t in old.name for t in ('-door-arch-', '-door-jamb'))):
            old['render_visible'] = False
            old['shadow'] = False
    door_y, spring, radius = y1 + .055, 1.94, .55
    curve = [(x + math.cos(a * math.pi / 12) * radius, spring + math.sin(a * math.pi / 12) * radius) for a in range(13)]
    leaf = [(x - radius, .06), (x + radius, .06)] + curve
    mesh(collection.name + '-arched-door-leaf', [(xx, door_y, zz) for xx, zz in leaf], [list(range(len(leaf)))], 'oak', False)
    for side in (-1, 1):
        box(collection.name + '-stone-jamb-' + str(side),
            (x + side * .64, y1 + .09, 1.02), (.18, .14, 1.96), 'stoneLight')
    for j in range(12):
        a, b = j * math.pi / 12 + .009, (j + 1) * math.pi / 12 - .009
        ring = [(x + math.cos(angle) * rr, spring + math.sin(angle) * rr)
                for rr, angle in [(.55, a), (.73, a), (.73, b), (.55, b)]]
        mesh(collection.name + '-arch-stone-' + str(j),
             [(xx, yy, zz) for yy in (y1 + .025, y1 + .16) for xx, zz in ring],
             [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4],
              [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], 'stoneLight')
    box(collection.name + '-arch-keystone', (x, y1 + .36, 2.60), (.22, .15, .27), 'stoneLight')
    for zz in (.58, 1.47):
        box(collection.name + '-door-strap-' + str(zz), (x, door_y + .028, zz), (.97, .035, .07), 'iron', False)
    box(collection.name + '-handle-plate', (x + .31, door_y + .033, 1.16), (.115, .045, .17), 'iron', False)
    box(collection.name + '-door-pull', (x + .31, door_y + .074, 1.15), (.055, .065, .13), 'gold', False)
    records.append({'owner': collection.name, 'finish': 'complete frontage',
                    'roofCoursesFollowSlope': True, 'archedDoorDepth': .105,
                    'layers': ['eave bead', 'rafter tails', 'ridge caps', 'side cornice',
                               'knee braces', 'window sills', 'shutter louvers', 'stone entrance']})

scene['exterior_craft_version'] = 67
scene['material_authoring_version'] = 67
scene['concept_architecture_version'] = 67
scene['sun_strength'] = .68
scene['ambient'] = .40
scene['ambient_color_json'] = json.dumps([.80, .92, 1.10])
scene['sun_color_json'] = json.dumps([1.15, 1.04, .84])
scene['bake_ao_samples'] = 16
scene['bake_ao_strength'] = .42
scene['bake_ao_radius'] = 1.6
scene['ground_shadow_resolution'] = 1536
scene['exterior_craft_review_json'] = json.dumps(records)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'), compress=True)
runpy.run_path(str(ROOT / 'tools/export-world-v3.py'), run_name='__main__')
print('Saved exterior craft on', len(records), 'lots;', roof_uvs,
      'roof faces mapped along their slopes; both lighting bakes required', flush=True)
