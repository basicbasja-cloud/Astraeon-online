"""Rebuild the twelve saved street frontages against the local RO3 references.

Original geometry and textures; no reference pixels or models are imported.
Keep lot XY, foundations, terrain, services and actors. Wall heights are
intentionally revised. Run once on source67, then rebake corner/floor lighting.
The replacement is repeatable using saved, unscaled structural vertices.
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
assert scene.get('exterior_craft_version') == 67
PREFIX = 'ro3-v68-'
primary_names = {c.name for c in bpy.data.collections if c.name.startswith('frontage-')}
bpy.data.batch_remove(ids=[obj for obj in bpy.data.objects if obj.name.startswith(PREFIX)
    and any(c.name in primary_names for c in obj.users_collection)])


def linear(color):
    values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
                 for v in values) + (1,)


def material(name, color, source=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = linear(color)
    if source:
        mat['texture_json'] = bpy.data.materials[source]['texture_json']
    return name


WALLS = {
    'residential': material('homeLimewash', '#e6dcc7', 'plaster'),
    'market': material('merchantLimewash', '#e8ddc8', 'plaster'),
    'workshop': material('workshopLimewash', '#dcd3bc', 'plaster'),
}
AWNING = material('shopAwningSage', '#77967b')
for name in ('roofClayWarm', 'roofClayOchre'):
    spec = json.loads(bpy.data.materials[name]['texture_json'])
    spec['worldSize'] = 2.4
    bpy.data.materials[name]['texture_json'] = json.dumps(spec)
FacadeKit = runpy.run_path(str(ROOT / 'tools/ro3-facade-kit-v68.py'))['FacadeKit']


records = []
removed = 0
for index, collection in enumerate(sorted(
        [c for c in bpy.data.collections if c.name.startswith('frontage-')], key=lambda c: c.name)):
    owner = collection
    root = bpy.data.objects[collection.name + '-placement']
    walls = next(o for o in collection.objects if o.name.startswith('plan-v44-') and o.name.endswith('-walls'))
    inv = root.matrix_world.inverted()
    points = [inv @ walls.matrix_world @ v.co for v in walls.data.vertices]
    x0, x1 = min(p.x for p in points), max(p.x for p in points)
    y0, y1 = min(p.y for p in points), max(p.y for p in points)
    oldtop = max(p.z for p in points)
    oldfloor = oldtop * .53
    x, w, d = (x0 + x1) / 2, x1 - x0, y1 - y0
    family = ('residential' if collection['family'] == 'residential' else
              'workshop' if any(t in collection.name for t in ('joiner', 'copper', 'cobbler')) else 'market')
    top, floor, door_h = {'residential': (6.3, 3.65, 2.8),
                         'market': (6.6, 3.8, 3.0), 'workshop': (6.1, 3.55, 2.75)}[family]
    wallmat = WALLS[family]
    roofmat = 'roofClayWarm' if family != 'market' else 'roofClayOchre'
    longrow = family != 'workshop' and index % 4 != 0
    name = collection.name

    def remap(z):
        if z <= .44:
            return z
        if z <= oldfloor:
            return .44 + (z - .44) * (floor - .44) / (oldfloor - .44)
        if z <= oldtop:
            return floor + (z - oldfloor) * (top - floor) / (oldtop - oldfloor)
        return top + (z - oldtop) * 1.25

    replacements = []
    for obj in list(collection.objects):
        if obj.type != 'MESH' or obj.name.startswith(PREFIX):
            continue
        n = obj.name
        wing = n.startswith('concept-v49-') and any(t in n for t in ('attached-wing', 'wing-'))
        core = n.startswith('side-v59-') and n.endswith('-lower-walls')
        if wing or core:
            if 'ro3_v68_original_vertices' not in obj:
                obj['ro3_v68_original_vertices'] = json.dumps([list(v.co) for v in obj.data.vertices])
            matrix = inv @ obj.matrix_world
            inverse = matrix.inverted()
            for vertex, original in zip(obj.data.vertices, json.loads(obj['ro3_v68_original_vertices'])):
                p = matrix @ Vector(original)
                p.z = remap(p.z)
                vertex.co = inverse @ p
            if obj.data.materials:
                m = obj.data.materials[0].name
                if m in ('plaster', *WALLS.values()):
                    obj.data.materials[0] = bpy.data.materials[wallmat]
                elif 'roof' in n or m in ('slate', 'terracotta'):
                    obj.data.materials[0] = bpy.data.materials[roofmat]
            continue
        if obj.get('role') == 'solid' or n == walls.name:
            continue
        replace = n.startswith(('family-v65-', 'frontage-v58-', 'side-v59-', 'attic-v62-',
                                'organic-v47-', 'exterior-v67-'))
        replace |= n.startswith('plan-v44-') and any(t in n for t in
            ('window', 'sill', 'shutter', 'door', 'floor-belt', 'floorbelt', 'corner', 'gable', 'roof', 'chimney'))
        replace |= n.startswith('quality-v46-') and any(t in n for t in
            ('eave', 'cornice', 'gallery', 'baluster', 'shop-awning', '-bay-', '-sign'))
        replace |= n.startswith('city-v48-') and any(t in n for t in ('window', 'shutter', 'oriel', 'chimney'))
        replace |= n.startswith('concept-v49-') and any(t in n for t in ('dormer', 'shop-awning', 'awning-brace'))
        if replace:
            replacements.append(obj)
            removed += 1
    bpy.data.batch_remove(ids=replacements)

    records.append(FacadeKit(owner, root).build(x0, x1, y0, y1, family, index,
        longrow=longrow, top=top, floor=floor, door_h=door_h, oldtop=oldtop))
    bays = records[-1]['upperWindowBays']
    print('RO3 facade', name, 'complete;', bays, 'upper bays;',
          'paired dormers' if longrow else 'front gable', flush=True)

bpy.data.batch_remove(ids=[data for data in bpy.data.meshes if not data.users])
scene['concept_architecture_version'] = 68
scene['frontage_family_version'] = 68
scene['ro3_facade_version'] = 68
scene['ro3_facade_review_json'] = json.dumps(records)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'authoring/wayfarer-spatial.blend'), compress=True)
runpy.run_path(str(ROOT / 'tools/export-world-v3.py'), run_name='__main__')
print('Saved RO3 facade68:', len(records), 'frontages;', removed, 'superseded pieces removed; rebake lighting', flush=True)
