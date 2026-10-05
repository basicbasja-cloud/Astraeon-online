"""Recompose existing frontage windows and roof silhouettes in saved source.

Run against wayfarer-spatial.blend. This is an envelope replacement inside the
existing twelve lots, not a town rebuild. Ground solids, service anchors,
navigation floors and patrols are retained. Re-running replaces this pass's
meshes rather than stacking detail or scaling the previous result.
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
assert scene.get('street_flora_ground_version') == 64, 'Use the saved flora64 source'
PREFIX = 'family-v65-'
for obj in list(bpy.data.objects):
    if obj.name.startswith(PREFIX):
        bpy.data.objects.remove(obj, do_unlink=True)
for data in list(bpy.data.meshes):
    if data.name.startswith(PREFIX) and not data.users:
        bpy.data.meshes.remove(data)


def linear(hex_color):
    values = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
                 for v in values) + (1,)


def finish(name, color, source):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = linear(color)
    material['texture_json'] = bpy.data.materials[source]['texture_json']
    return name


WALLS = {
    'residential': finish('homeLimewash', '#e4cfad', 'plaster'),
    'market': finish('merchantLimewash', '#d9bc8d', 'plaster'),
    'workshop': finish('workshopLimewash', '#bac9c0', 'plaster'),
}
ROOFS = [finish('roofClayWarm', '#aa6348', 'terracotta'),
         finish('roofClayOchre', '#bb875b', 'terracotta'),
         finish('roofSlateTeal', '#447474', 'slate'),
         finish('roofSlateBlue', '#3e6484', 'slate')]
GLASS = finish('frontageGlazing', '#417788', 'glass')
owner = root = None


def mesh(name, vertices, faces, material, shadow=True):
    data = bpy.data.meshes.new(PREFIX + name)
    data.from_pydata(vertices, [], faces)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(data)
    bm.free()
    data.materials.append(bpy.data.materials[material])
    data.uv_layers.new(name='PhysicalUV')
    scale = json.loads(bpy.data.materials[material]['texture_json']).get('worldSize', 3)
    for face in data.polygons:
        for li in face.loop_indices:
            p = data.vertices[data.loops[li].vertex_index].co
            n = face.normal
            data.uv_layers.active.data[li].uv = ((p.x / scale, p.y / scale)
                if abs(n.z) > .65 else (p.y / scale, p.z / scale)
                if abs(n.x) > abs(n.y) else (p.x / scale, p.z / scale))
    obj = bpy.data.objects.new(PREFIX + name, data)
    owner.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj['role'] = 'overhead'
    obj['shadow'] = shadow
    return obj


def box(name, center, size, material, shadow=True):
    x, y, z = center
    a, b, h = [v / 2 for v in size]
    return mesh(name, [(x + i * a, y + j * b, z + k * h)
                      for k in (-1, 1) for j in (-1, 1) for i in (-1, 1)],
                [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
                 [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]], material, shadow)


def beam(name, a, b, width, material):
    a, b = Vector(a), Vector(b)
    direction = (b - a).normalized()
    u = direction.cross(Vector((0, 1, 0)))
    if u.length < .01:
        u = direction.cross(Vector((1, 0, 0)))
    u.normalize()
    v = direction.cross(u).normalized()
    return mesh(name, [tuple(p + i * u * width / 2 + j * v * width / 2)
                      for p in (a, b) for i, j in [(-1, -1), (1, -1), (1, 1), (-1, 1)]],
                [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
                 [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], material)


def window(name, x, y, z, width, height, trim):
    """Open facade, splayed reveal, recessed glazing, projecting frame."""
    a, h = width / 2, height / 2
    outer = [(x - a, y + .13, z - h), (x + a, y + .13, z - h),
             (x + a, y + .13, z + h), (x - a, y + .13, z + h)]
    inner = [(x - a + .10, y - .22, z - h + .10),
             (x + a - .10, y - .22, z - h + .10),
             (x + a - .10, y - .22, z + h - .10),
             (x - a + .10, y - .22, z + h - .10)]
    mesh(name + '-splayed-reveal', outer + inner,
         [[i, (i + 1) % 4, (i + 1) % 4 + 4, i + 4] for i in range(4)], trim)
    box(name + '-glass', (x, y - .215, z), (width - .19, .025, height - .19), GLASS, False)
    for side in (-1, 1):
        box(name + '-jamb-' + str(side), (x + side * (a + .055), y + .18, z),
            (.15, .30, height + .25), trim)
    for dz in (-h - .055, h + .055):
        box(name + '-lintel-' + str(dz), (x, y + .18, z + dz),
            (width + .24, .30, .14), trim)
    box(name + '-deep-sill', (x, y + .25, z - h - .11),
        (width + .38, .48, .15), 'stoneLight')
    box(name + '-mullion', (x, y - .17, z), (.065, .07, height - .18), 'stoneLight', False)
    box(name + '-transom', (x, y - .17, z - .13),
        (width - .18, .07, .055), 'stoneLight', False)


records = []
for index, collection in enumerate(sorted(
        [c for c in bpy.data.collections if c.name.startswith('frontage-')],
        key=lambda c: c.name)):
    owner = collection
    root = bpy.data.objects[collection.name + '-placement']
    inv = root.matrix_world.inverted()
    walls = next(o for o in collection.objects if o.name.endswith('-walls'))
    points = [inv @ walls.matrix_world @ v.co for v in walls.data.vertices]
    x0, x1 = min(p.x for p in points), max(p.x for p in points)
    y0, y1 = min(p.y for p in points), max(p.y for p in points)
    h = max(p.z for p in points)
    x, w, d = (x0 + x1) / 2, x1 - x0, y1 - y0
    family = ('residential' if collection['family'] == 'residential' else
              'workshop' if any(t in collection.name for t in ('joiner', 'copper', 'cobbler'))
              else 'market')
    wallmat = WALLS[family]
    roofmat = ROOFS[(0 if family == 'residential' else 2 if family == 'workshop' else 1)
                    if index % 3 else 3]
    trim = 'oak' if family == 'residential' else 'timber'
    front = y1 + [.76, .89, .82][index % 3]
    bottom, top = h * .53, h + .04
    window_h = min(1.82, (top - bottom) * .70)
    z = (top + bottom) / 2 + .06
    lo, hi = z - window_h / 2, z + window_h / 2
    window_w = min(1.72, w * .235)
    centers = [x - w * .29, x + w * .29]
    for obj in list(collection.objects):
        if obj.type != 'MESH' or obj.name.startswith(PREFIX):
            continue
        name = obj.name
        replace = (name.startswith('frontage-v58-') and any(t in name for t in
                   ('-pier-', '-window-base-', '-window-head-', '-end-pier')))
        replace |= (name.startswith('city-v48-') and any(t in name for t in
                    ('window-', 'shutter', 'oriel')))
        replace |= ('-dormer-' in name)
        if replace:
            obj['render_visible'] = False
            obj['shadow'] = False
        if obj.get('render_visible', True):
            material = obj.data.materials[0].name
            if material == 'plaster':
                obj.data.materials[0] = bpy.data.materials[wallmat]
            elif material in ('slate', 'terracotta') or material in ROOFS:
                obj.data.materials[0] = bpy.data.materials[roofmat]
    last = x0 - .115
    for j, xx in enumerate(centers):
        left, right = xx - window_w / 2, xx + window_w / 2
        box(collection.name + '-pier-' + str(j), ((last + left) / 2, front, (top + bottom) / 2),
            (left - last, .24, top - bottom), wallmat)
        box(collection.name + '-below-' + str(j), (xx, front, (bottom + lo) / 2),
            (window_w, .24, lo - bottom), wallmat)
        box(collection.name + '-above-' + str(j), (xx, front, (hi + top) / 2),
            (window_w, .24, top - hi), wallmat)
        window(collection.name + '-window-' + str(j), xx, front, z, window_w, window_h, trim)
        if family == 'residential':
            for side in (-1, 1):
                box(collection.name + '-shutter-' + str((j, side)),
                    (xx + side * (window_w / 2 + .31), front + .14, z),
                    (.33, .12, window_h - .04), 'oak')
        last = right
    box(collection.name + '-end-pier', ((last + x1 + .115) / 2, front, (top + bottom) / 2),
        (x1 + .115 - last, .24, top - bottom), wallmat)

    # One roof-owned cross gable replaces the competing small dormer boxes.
    # Its cheeks meet the actual curved roof and its opening faces the slope.
    roofs = [o for o in collection.objects if '-curved-roof-' in o.name]
    # Preserve each roof's authored uncut geometry/UVs for repeatable replacement.
    for obj in roofs:
        if obj.get('family_v65_roof_base_json'):
            baseline = json.loads(obj['family_v65_roof_base_json'])
            obj.data.clear_geometry()
            obj.data.from_pydata(baseline['vertices'], [], baseline['faces'])
            obj.data.uv_layers.new(name='PhysicalUV')
            for face, uvs in zip(obj.data.polygons, baseline['uvs']):
                for li, uv in zip(face.loop_indices, uvs):
                    obj.data.uv_layers.active.data[li].uv = uv
        else:
            obj['family_v65_roof_base_json'] = json.dumps({
                'vertices': [list(v.co) for v in obj.data.vertices],
                'faces': [list(f.vertices) for f in obj.data.polygons],
                'uvs': [[list(obj.data.uv_layers.active.data[li].uv) for li in f.loop_indices]
                        for f in obj.data.polygons]})
        obj.data.update()
    roof_points = [inv @ o.matrix_world @ v.co for o in roofs for v in o.data.vertices]
    profile = sorted({(round(p.x, 5), round(p.z, 5)) for p in roof_points})
    def roof_at(xx):
        for (a, za), (b, zb) in zip(profile, profile[1:]):
            if a - 1e-4 <= xx <= b + 1e-4 and b > a:
                return za + (zb - za) * max(0, min(1, (xx - a) / (b - a)))
        raise ValueError(('Outside roof profile', xx))
    side = -1 if index % 2 else 1
    face_x = x + side * w * .43
    back_x = x + side * w * .21
    cy = (y0 + y1) / 2 + (.42 if index % 2 else -.38)
    half = min(1.03, d * .20)
    base = roof_at(face_x) - .15
    eave = max(roof_at(back_x) + .18, base + 1.65)
    peak = eave + .83
    # Build the cross gable in a temporary local (u=Y, v=outward X) frame,
    # then map every new component back to the unchanged building root.
    before = set(bpy.data.objects)
    prefix = collection.name + '-cross-gable'
    depth = abs(back_x - face_x)
    yy = 0
    half_window, win_lo, win_hi = half * .58, base + .25, eave - .22
    box(prefix + '-left-pier', (-(half + half_window) / 2, yy, (base + eave) / 2),
        (half - half_window, .18, eave - base), wallmat)
    box(prefix + '-right-pier', ((half + half_window) / 2, yy, (base + eave) / 2),
        (half - half_window, .18, eave - base), wallmat)
    box(prefix + '-base', (0, yy, (base + win_lo) / 2),
        (half_window * 2, .18, win_lo - base), wallmat)
    box(prefix + '-head', (0, yy, (win_hi + eave) / 2),
        (half_window * 2, .18, eave - win_hi), wallmat)
    window(prefix, 0, yy, (win_lo + win_hi) / 2, half_window * 2, win_hi - win_lo, trim)
    mesh(prefix + '-gable', [(-half, 0, eave), (half, 0, eave), (0, 0, peak)], [[0, 1, 2]], wallmat)
    mesh(prefix + '-back', [(-half, -depth, roof_at(back_x) - .15),
         (half, -depth, roof_at(back_x) - .15), (half, -depth, eave),
         (0, -depth, peak), (-half, -depth, eave)], [[0, 1, 2, 3, 4]], wallmat)
    for sign in (-1, 1):
        mesh(prefix + '-cheek-' + str(sign),
            [(sign * half, 0, base), (sign * half, -depth, roof_at(back_x) - .15),
             (sign * half, -depth, eave), (sign * half, 0, eave)], [[0, 1, 2, 3]], wallmat)
        mesh(prefix + '-roof-' + str(sign),
            [(sign * (half + .22), .27, eave), (sign * (half + .22), -depth - .15, eave),
             (0, -depth - .15, peak), (0, .27, peak)], [[0, 1, 2, 3]], roofmat)
        beam(prefix + '-verge-' + str(sign), (sign * (half + .19), .29, eave),
             (0, .29, peak), .13, trim)
    beam(prefix + '-ridge', (0, .28, peak + .04), (0, -depth - .14, peak + .04), .16, roofmat)
    for obj in set(bpy.data.objects) - before:
        for vertex in obj.data.vertices:
            u, v, zz = vertex.co
            vertex.co = (face_x + side * v, cy - side * u, zz)
        obj.data.update()
    # Cut the occupied dormer rectangle out of the existing roof strips. This
    # prevents the original slope crossing the glazing/cheeks. The remaining
    # planes keep the original affine UV mapping, roof pitch and silhouette.
    cut_x0, cut_x1 = sorted((face_x, back_x))
    cut_y0, cut_y1 = cy - half, cy + half
    for obj in roofs:
        data = obj.data
        points = [inv @ obj.matrix_world @ v.co for v in data.vertices]
        ax, bx = min(p.x for p in points), max(p.x for p in points)
        ay, by = min(p.y for p in points), max(p.y for p in points)
        if bx <= cut_x0 or ax >= cut_x1 or by <= cut_y0 or ay >= cut_y1:
            continue
        face = data.polygons[0]
        p0, p1, p2 = [points[i] for i in face.vertices[:3]]
        uv0, uv1, uv2 = [data.uv_layers.active.data[li].uv.copy() for li in face.loop_indices[:3]]
        v0, v1 = p1 - p0, p2 - p0
        det = v0.x * v1.y - v0.y * v1.x
        def mapped_uv(px, py):
            dx, dy = px - p0.x, py - p0.y
            u = (dx * v1.y - dy * v1.x) / det
            v = (v0.x * dy - v0.y * dx) / det
            return uv0 + u * (uv1 - uv0) + v * (uv2 - uv0)
        xs = sorted({ax, bx, max(ax, cut_x0), min(bx, cut_x1)})
        ys = sorted({ay, by, max(ay, cut_y0), min(by, cut_y1)})
        vertices, faces, uvs = [], [], []
        to_data = obj.matrix_world.inverted() @ root.matrix_world
        for a, b in zip(xs, xs[1:]):
            for c, dd in zip(ys, ys[1:]):
                if b - a < 1e-6 or dd - c < 1e-6:
                    continue
                if cut_x0 < (a + b) / 2 < cut_x1 and cut_y0 < (c + dd) / 2 < cut_y1:
                    continue
                corners = [(a, c), (b, c), (b, dd), (a, dd)]
                start = len(vertices)
                vertices.extend(to_data @ Vector((px, py, roof_at(px))) for px, py in corners)
                faces.append([start + i for i in range(4)])
                uvs.append([mapped_uv(px, py) for px, py in corners])
        data.clear_geometry()
        data.from_pydata(vertices, [], faces)
        data.uv_layers.new(name='PhysicalUV')
        for face, coords in zip(data.polygons, uvs):
            for li, uv in zip(face.loop_indices, coords):
                data.uv_layers.active.data[li].uv = uv
        data.update()
    records.append({'owner': collection.name, 'family': family, 'windowWidth': window_w,
                    'windowHeight': window_h, 'revealDepth': .35, 'roofMaterial': roofmat,
                    'crossGable': True, 'groundFootprintRetained': True})

scene['frontage_family_version'] = 65
scene['concept_architecture_version'] = 65
scene['frontage_family_review_json'] = json.dumps(records)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'), compress=True)
runpy.run_path(str(ROOT / 'tools/export-world-v3.py'), run_name='__main__')
print('Saved twelve recomposed frontage envelopes, splayed windows and roof-owned cross gables;',
      'corner and ground bakes required', flush=True)
