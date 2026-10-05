"""Original RO3-reference facade modules shared by primary and infill lots.

Only defines geometry helpers. Call FacadeKit for an existing saved collection
and its editable placement/model frame; this module never saves or rebuilds town.
"""
import json
import math
import bmesh
import bpy
from mathutils import Matrix, Vector

WALLS={'residential':'homeLimewash','market':'merchantLimewash','workshop':'workshopLimewash'}
AWNING='shopAwningSage'

class FacadeKit:
    def __init__(self, owner, root):
        self.owner, self.root = owner, root
        self.prefix = 'ro3-v68-'
        self.side_windows = {}
        self.ground_front = None
        self.awning_rise = 0


    def mesh(self, name, points, faces, mat, shadow=True):
        data = bpy.data.meshes.new(self.prefix + name)
        data.from_pydata(points, [], faces)
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        bm.to_mesh(data)
        bm.free()
        data.materials.append(bpy.data.materials[mat])
        data.uv_layers.new(name='PhysicalUV')
        scale = json.loads(bpy.data.materials[mat].get('texture_json', '{}')).get('worldSize', 2.4)
        for face in data.polygons:
            for li in face.loop_indices:
                p = data.vertices[data.loops[li].vertex_index].co
                n = face.normal
                data.uv_layers.active.data[li].uv = ((p.x / scale, p.y / scale)
                    if abs(n.z) > .65 else (p.y / scale, p.z / scale)
                    if abs(n.x) > abs(n.y) else (p.x / scale, p.z / scale))
        obj = bpy.data.objects.new(self.prefix + name, data)
        self.owner.objects.link(obj)
        obj.parent = self.root
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj['role'] = 'decorative'
        obj['shadow'] = shadow
        return obj

    def box(self, name, center, size, mat, shadow=True):
        x, y, z = center
        a, b, h = [v / 2 for v in size]
        return self.mesh(name, [(x + i * a, y + j * b, z + k * h)
                          for k in (-1, 1) for j in (-1, 1) for i in (-1, 1)],
                    [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
                     [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]], mat, shadow)

    def beam(self, name, a, b, width, mat='timber'):
        a, b = Vector(a), Vector(b)
        direction = (b - a).normalized()
        u = direction.cross(Vector((0, 1, 0)))
        if u.length < .01:
            u = direction.cross(Vector((1, 0, 0)))
        u.normalize()
        v = direction.cross(u).normalized()
        obj = self.mesh(name, [tuple(p + i * u * width / 2 + j * v * width / 2)
                         for p in (a, b) for i, j in [(-1, -1), (1, -1), (1, 1), (-1, 1)]],
                   [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
                    [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], mat)
        for face in obj.data.polygons:
            for li in face.loop_indices:
                p = obj.data.vertices[obj.data.loops[li].vertex_index].co - a
                obj.data.uv_layers.active.data[li].uv = (p.dot(u) / 2.4, p.dot(direction) / 2.4)
        return obj

    def window(self, name, x, y, z, width, height, trim='timber', recess=.215, low=False):
        """Nine small lights. Upper reveals pass through real facade openings.

        Ground glazing sits ahead of the retained collision core, with frames
        projecting <= .16; overhead reveals may project further.
        """
        a, h = width / 2, height / 2
        front = .12 if low else .16
        outer = [(x - a, y + front, z - h), (x + a, y + front, z - h),
                 (x + a, y + front, z + h), (x - a, y + front, z + h)]
        inner = [(x - a + .09, y - recess, z - h + .09),
                 (x + a - .09, y - recess, z - h + .09),
                 (x + a - .09, y - recess, z + h - .09),
                 (x - a + .09, y - recess, z + h - .09)]
        self.mesh(name + '-reveal', outer + inner,
             [[i, (i + 1) % 4, (i + 1) % 4 + 4, i + 4] for i in range(4)], trim)
        self.box(name + '-glass', (x, y - recess + .005, z),
            (width - .18, .02, height - .18), 'frontageGlazing', False)
        depth, yy = (.12, y + .10) if low else (.24, y + .16)
        for side in (-1, 1):
            self.box(name + '-jamb-' + str(side), (x + side * a, yy, z),
                (.14, depth, height + .12), trim)
            self.box(name + '-lintel-' + str(side), (x, yy, z + side * h),
                (width + .14, depth, .14), trim)
        for j in (1, 2):
            self.box(name + '-mullion-' + str(j), (x - (width - .18) / 2 + j * (width - .18) / 3,
                y - recess + .025, z), (.055, .04, height - .18), 'stoneLight', False)
            self.box(name + '-transom-' + str(j), (x, y - recess + .025,
                z - (height - .18) / 2 + j * (height - .18) / 3),
                (width - .18, .04, .055), 'stoneLight', False)
        self.box(name + '-sill', (x, y + (.10 if low else .22), z - h - .06),
            (width + .28, .12 if low else .40, .14), 'stoneLight')

    def upper_face(self, name, width, floor, top, centers, wallmat, origin, angle, wh=1.52, ww=1.08):
        before = set(self.owner.objects)
        z = (floor + top) / 2 + .04
        last = -width / 2
        for j, xx in enumerate(centers):
            left, right = xx - ww / 2, xx + ww / 2
            self.box(name + '-pier-' + str(j), ((last + left) / 2, 0, (top + floor) / 2),
                (left - last, .24, top - floor), wallmat)
            self.box(name + '-base-' + str(j), (xx, 0, (floor + z - wh / 2) / 2),
                (ww, .24, z - wh / 2 - floor), wallmat)
            self.box(name + '-head-' + str(j), (xx, 0, (z + wh / 2 + top) / 2),
                (ww, .24, top - z - wh / 2), wallmat)
            self.window(name + '-window-' + str(j), xx, 0, z, ww, wh)
            last = right
        self.box(name + '-end', ((last + width / 2) / 2, 0, (top + floor) / 2),
            (width / 2 - last, .24, top - floor), wallmat)
        posts = [-width / 2 + .12, width / 2 - .12]
        posts += [(a + b) / 2 for a, b in zip(centers, centers[1:])]
        for j, xx in enumerate(posts):
            self.box(name + '-post-' + str(j), (xx, .13, (floor + top) / 2),
                (.24, .22, top - floor), 'timber')
        for zz, thick in ((floor, .25), (top, .26)):
            self.box(name + '-belt-' + str(zz), (0, .13, zz), (width + .12, .24, thick), 'timber')
        if width >= 2.5:
            for side in (-1, 1):
                xx = side * (width / 2 - .24)
                self.beam(name + '-knee-' + str(side), (xx, .12, floor + .30),
                     (xx - side * .48, .12, floor + .86), .15)
        rotation = Matrix.Rotation(angle, 4, 'Z')
        for obj in set(self.owner.objects) - before:
            for v in obj.data.vertices:
                v.co = rotation @ v.co + Vector((origin[0], origin[1], 0))

    def ground_frontage(self, name, x, w, y1, family, floor, door_h, front):
        # Fit the ground frontage to its actual traced front edge.
        if self.ground_front is not None:
            x, w = self.ground_front
        before = set(self.owner.objects)
        narrow = w < 4.7
        doorx = x - w * .23 if narrow else x - w * .22 if family == 'market' else x
        doorw = min(1.32, w * .32) if narrow else 1.55 if family == 'market' else 1.32
        doorz = .44 + door_h / 2
        self.box(name + '-door-leaf', (doorx, y1 + .035, doorz), (doorw, .03, door_h), 'oak', False)
        for side in (-1, 1):
            self.box(name + '-door-post-' + str(side), (doorx + side * (doorw / 2 + .12), y1 + .09, doorz),
                (.24, .14, door_h + .20), 'timber')
        self.box(name + '-door-lintel', (doorx, y1 + .09, .44 + door_h + .10),
            (doorw + .52, .14, .22), 'timber')
        for j in range(1, 7):
            self.box(name + '-door-board-' + str(j), (doorx - doorw / 2 + j * doorw / 7, y1 + .057, doorz),
                (.028, .012, door_h - .08), 'timber', False)
        for zz in (.95, 2.35):
            self.box(name + '-door-iron-' + str(zz), (doorx, y1 + .075, zz), (doorw - .13, .025, .07), 'iron', False)
        self.box(name + '-door-pull', (doorx + doorw * .27, y1 + .105, 1.55), (.055, .06, .18), 'gold', False)
        # Trade board under the upper windows, replacing signs across old glazing.
        self.box(name + '-trade-board', (doorx, front + .22, floor + .32), (.68, .10, .26), 'oak')
        for side in (-1, 1):
            self.box(name + '-trade-hook-' + str(side), (doorx + side * .23, front + .22, floor + .52),
                (.04, .04, .20), 'iron')
        self.box(name + '-trade-inlay', (doorx, front + .28, floor + .32), (.20, .025, .08), 'gold', False)
        for side in (-1, 1):
            self.box(name + '-ground-corner-' + str(side), (x + side * (w / 2 - .16), y1 + .075, (.44 + floor) / 2),
                (.32, .15, floor - .44), 'timber')
        groundcenters = [x + w * .23] if narrow else [x + w * .22] if family == 'market' else [x - w * .30, x + w * .30]
        for j, xx in enumerate(groundcenters):
            self.window(name + '-ground-window-' + str(j), xx, y1, 1.99,
                   min(1.02, w * .30) if narrow else 1.52 if family == 'market' else 1.02,
                   1.43, recess=-.025, low=True)
        if family == 'market':
            aw = 2.42
            for j in range(6):
                xa = x + w * .22 - aw / 2 + j * aw / 6
                self.mesh(name + '-awning-' + str(j), [(xa, y1 + .04, 3.38),
                    (xa + aw / 6, y1 + .04, 3.38), (xa + aw / 6, y1 + 1.24, 3.08),
                    (xa, y1 + 1.24, 3.08)], [[0, 1, 2, 3]], AWNING if j % 2 else 'homeLimewash')
                self.box(name + '-awning-valance-' + str(j), (xa + aw / 12, y1 + 1.24, 2.98),
                    (aw / 6, .06, .20), AWNING if j % 2 else 'homeLimewash')
            for side in (-1, 1):
                self.beam(name + '-awning-strut-' + str(side), (x + w * .22 + side * aw / 2, y1 + .06, 2.65),
                     (x + w * .22 + side * aw / 2, y1 + 1.20, 3.08), .07, 'iron')

        if self.awning_rise:
            for obj in set(self.owner.objects) - before:
                if '-awning-' in obj.name:
                    for vertex in obj.data.vertices:vertex.co.z += self.awning_rise

    def build(self, x0, x1, y0, y1, family, index=0, longrow=None, top=None, floor=None, door_h=None, oldtop=None):
        name = self.owner.name
        x, w, d = (x0 + x1) / 2, x1 - x0, y1 - y0
        policy = {'residential': (6.3, 3.65, 2.8), 'market': (6.6, 3.8, 3.0), 'workshop': (6.1, 3.55, 2.75)}[family]
        top = policy[0] if top is None else top
        floor = policy[1] if floor is None else floor
        door_h = policy[2] if door_h is None else door_h
        oldtop = top if oldtop is None else oldtop
        longrow = (w >= 4.7 and family != 'workshop' and index % 4 != 0) if longrow is None else longrow
        wallmat = WALLS[family]
        roofmat = 'roofClayWarm' if family != 'market' else 'roofClayOchre'
        # Small upper-floor jetty; real window openings on all four faces.
        front, back = y1 + .42, y0 - .12
        sides = (x0 - .12, x1 + .12)
        bays = 4 if w >= 6.5 else 3 if w >= 4.7 else 2
        centers = [(j - (bays - 1) / 2) * (w - 1.35) / bays for j in range(bays)]
        self.upper_face(name + '-front', w + .24, floor, top, centers, wallmat, (x, front), 0, ww=min(1.08, (w - 1.35) / bays - .20))
        self.upper_face(name + '-rear', w + .24, floor, top, centers, wallmat, (x, back), math.pi, ww=min(1.08, (w - 1.35) / bays - .20))
        sidewidth = front - back
        sidecenters = [-sidewidth * .25, sidewidth * .25]
        for side in (-1, 1):
            # The retained attached wing occupies the rear half of this side.
            usable = self.side_windows.get(side, [-sidewidth * .25] if name == 'frontage-riverside' and side == 1 else sidecenters)
            self.upper_face(name + '-side-' + str(side), sidewidth, floor, top,
                       usable, wallmat, (sides[0 if side < 0 else 1], (front + back) / 2),
                       -side * math.pi / 2)
        self.box(name + '-jetty-soffit', (x, (back + front) / 2, floor - .09),
            (w + .24, front - back, .18), 'timber')
        for j in range(9):
            xx = x0 + .2 + j * (w - .4) / 8
            self.beam(name + '-jetty-corbel-' + str(j), (xx, y1 + .04, floor - .52),
                 (xx, front + .04, floor - .17), .14)
        # Small scalloped wood frieze below the upper floor, visible in 04_08_45.
        for j in range(16):
            xx = x0 + .23 + j * (w - .46) / 15
            arc = [(xx + .12 * math.cos(k * math.pi / 6),
                    floor - .19 - .12 * math.sin(k * math.pi / 6)) for k in range(7)]
            self.mesh(name + '-scalloped-frieze-' + str(j),
                 [(px, yy, pz) for yy in (front + .06, front + .18) for px, pz in arc],
                 [list(range(6, -1, -1)), list(range(7, 14))] +
                 [[k, k + 1, k + 8, k + 7] for k in range(6)], 'timber')
        self.ground_frontage(name, x, w, y1, family, floor, door_h, front)

        # Main roof: ridge parallel to long facades, paired dormers below it.
        rx0, rx1, ry0, ry1 = x0 - .46, x1 + .46, y0 - .46, y1 + .96
        pitch = math.radians(42 if longrow else 48)
        center = (ry0 + ry1) / 2 if longrow else x
        half = (ry1 - ry0) / 2 if longrow else (rx1 - rx0) / 2
        eave, peak = top + .22, top + .22 + half * math.tan(pitch)

        def roof_at(q):
            distance = abs(q - center)
            kick = .08 * max(0, (distance - half + .30) / .30)
            return peak - distance * math.tan(pitch) + kick

        cuts = []
        dormer_record = []
        if longrow:
            for j, dx in enumerate((x - w * .24, x + w * .24)):
                ya, yb, a = y1 - .60, y1 + .52, .64
                base = roof_at(yb) - .12
                deave = max(base + 1.20, roof_at(ya) + .15)
                dpeak = deave + .70
                assert dpeak < peak, (name, dpeak, peak)
                cuts.append((dx - a, dx + a, ya, yb))
                dn = name + '-dormer-' + str(j)
                # Front face has a genuine window aperture.
                self.upper_face(dn, a * 2, base, deave, [0], wallmat, (dx, yb), 0, wh=.90, ww=.82)
                # Narrower glazing opening than the storeys avoids negative panels.
                for side in (-1, 1):
                    xx = dx + side * a
                    self.mesh(dn + '-cheek-' + str(side), [(xx, ya, roof_at(ya) - .12),
                        (xx, yb, base), (xx, yb, deave), (xx, ya, deave)], [[0, 1, 2, 3]], wallmat)
                self.mesh(dn + '-gable', [(dx - a, yb, deave), (dx + a, yb, deave),
                    (dx, yb, dpeak)], [[0, 1, 2]], wallmat)
                self.mesh(dn + '-back', [(dx - a, ya, roof_at(ya) - .12),
                    (dx + a, ya, roof_at(ya) - .12), (dx + a, ya, deave),
                    (dx, ya, dpeak), (dx - a, ya, deave)], [[0, 1, 2, 3, 4]], wallmat)
                for side in (-1, 1):
                    xx = dx + side * (a + .13)
                    obj = self.mesh(dn + '-roof-' + str(side), [(dx, ya - .10, dpeak + .08),
                        (xx, ya - .10, deave - .06), (xx, yb + .16, deave - .06),
                        (dx, yb + .16, dpeak + .08)], [[0, 1, 2, 3]], roofmat)
                    roof_angle = math.atan2(dpeak + .08 - deave + .06, a + .13)
                    for face in obj.data.polygons:
                        for li in face.loop_indices:
                            p = obj.data.vertices[obj.data.loops[li].vertex_index].co
                            obj.data.uv_layers.active.data[li].uv = (
                                p.y / 2.4, -abs(p.x - dx) / math.cos(roof_angle) / 2.4)
                    self.beam(dn + '-verge-' + str(side), (dx, yb + .18, dpeak), (xx, yb + .18, deave - .1), .17)
                self.beam(dn + '-kingpost', (dx, yb + .10, deave), (dx, yb + .10, dpeak), .13)
                dormer_record.append({'centerX': dx, 'base': base, 'eave': deave, 'peak': dpeak})

        # Continuous roof coordinates, with physical holes beneath dormers.
        xs = sorted(set([rx0, rx1] + ([x, rx0 + .30, rx1 - .30] if not longrow else []) + [q for cut in cuts for q in cut[:2]]))
        ys = sorted(set([ry0, ry1] + ([center, ry0 + .30, ry1 - .30] if longrow else []) + [q for cut in cuts for q in cut[2:]]))
        roofpoints, rooffaces = [], []
        for xa, xb in zip(xs, xs[1:]):
            for ya, yb in zip(ys, ys[1:]):
                if any(a < (xa + xb) / 2 < b and c < (ya + yb) / 2 < d for a, b, c, d in cuts):
                    continue
                start = len(roofpoints)
                roofpoints.extend((xx, yy, roof_at(yy if longrow else xx))
                                  for xx, yy in ((xa, ya), (xb, ya), (xb, yb), (xa, yb)))
                rooffaces.append([start + i for i in range(4)])
        roof = self.mesh(name + '-main-roof', roofpoints, rooffaces, roofmat)
        for face in roof.data.polygons:
            for li in face.loop_indices:
                p = roof.data.vertices[roof.data.loops[li].vertex_index].co
                q = p.y if longrow else p.x
                roof.data.uv_layers.active.data[li].uv = (
                    (p.x if longrow else p.y) / 2.4, -abs(q - center) / math.cos(pitch) / 2.4)
        roof['role'] = 'overhead'
        for side in (-1, 1):
            # Triangular closed end, timber kingpost and fan braces.
            if longrow:
                xx = rx0 + .28 if side < 0 else rx1 - .28
                triangle = [(xx, ry0 + .28, eave + .25), (xx, ry1 - .28, eave + .25), (xx, center, peak)]
                a, b = (xx, ry0, eave), (xx, ry1, eave)
                ridgepoint = (xx, center, peak)
            else:
                yy = ry0 + .28 if side < 0 else ry1 - .28
                triangle = [(rx0 + .28, yy, eave + .25), (rx1 - .28, yy, eave + .25), (x, yy, peak)]
                a, b = (rx0, yy, eave), (rx1, yy, eave)
                ridgepoint = (x, yy, peak)
            self.mesh(name + '-end-gable-' + str(side), triangle, [[0, 1, 2]], wallmat)
            self.beam(name + '-verge-a-' + str(side), a, ridgepoint, .24)
            self.beam(name + '-verge-b-' + str(side), b, ridgepoint, .24)
            self.beam(name + '-gable-belt-' + str(side), a, b, .24)
            middle = tuple((Vector(a) + Vector(b)) / 2)
            if not longrow and side > 0:
                az = eave + .92
                self.beam(name + '-gable-kingpost-low', middle, (x, middle[1], az - .60), .22)
                self.beam(name + '-gable-kingpost-high', (x, middle[1], az + .60), ridgepoint, .22)
            else:
                self.beam(name + '-gable-kingpost-' + str(side), middle, ridgepoint, .22)
            for j, end in enumerate((a, b)):
                self.beam(name + '-gable-fan-' + str((side, j)),
                     tuple(Vector(middle).lerp(Vector(end), .60)),
                     tuple(Vector(middle).lerp(Vector(ridgepoint), .58)), .18)
            if longrow:
                self.beam(name + '-eave-' + str(side), (rx0, ry0 if side < 0 else ry1, eave),
                     (rx1, ry0 if side < 0 else ry1, eave), .25)
            else:
                self.beam(name + '-eave-' + str(side), (rx0 if side < 0 else rx1, ry0, eave),
                     (rx0 if side < 0 else rx1, ry1, eave), .25)
        if not longrow:
            # Attic glass sits ahead of the triangular gable; opened timber shutters.
            az = eave + .92
            self.window(name + '-attic-window', x, ry1 - .24, az, .90, 1.02, recess=-.035)
            for side in (-1, 1):
                shutter = self.box(name + '-attic-shutter-' + str(side), (x + side * .69, ry1 - .04, az), (.35, .08, .97), 'oak')
                for j in range(4):
                    self.box(name + '-shutter-rail-' + str((side, j)), (x + side * .69, ry1 + .005, az - .34 + j * .225),
                        (.31, .025, .065), 'timber')
        ridge_a, ridge_b = ((rx0, center, peak + .03), (rx1, center, peak + .03)) if longrow else (
            (x, ry0, peak + .03), (x, ry1, peak + .03))
        self.beam(name + '-ridge-cap', ridge_a, ridge_b, .20, roofmat)
        cx, cy = x - w * .27, y0 + d * .22
        base = roof_at(cy if longrow else cx) - .18
        self.box(name + '-chimney', (cx, cy, base + .65), (.62, .66, 1.30), 'stoneLight')
        self.box(name + '-chimney-cap', (cx, cy, base + 1.32), (.80, .84, .18), 'stoneLight')
        self.box(name + '-chimney-mouth', (cx, cy, base + 1.42), (.43, .47, .02), 'iron', False)
        return {'owner': name, 'family': family,
            'reference': '04_08_00 / 04_08_45' if longrow else '04_08_34 / 04_08_45',
            'ridgeAlongFacade': longrow, 'roofPitchDegrees': math.degrees(pitch),
            'wallHeight': top, 'groundFloorTop': floor, 'doorLeafHeight': door_h,
            'humanHeightWorld': 2 * 92 / 76, 'doorToHumanRatio': door_h / (2 * 92 / 76),
            'upperWindowBays': bays, 'upperWindowSize': [min(1.08, (w - 1.35) / bays - .20), 1.52],
            'panes': [3, 3], 'jettyProjection': .42, 'groundProjectionMax': .16,
            'mainRoofPeak': peak, 'dormers': dormer_record,
            'lotWidth': w, 'lotDepth': d, 'oldWallHeight': oldtop,
            'wingJoinedSideWindowOmitted': name == 'frontage-riverside'}
