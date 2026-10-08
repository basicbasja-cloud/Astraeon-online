"""Blender authoring-only walk proof; never produces runtime sprite atlases.

blender --background --factory-startup --python tools/build-swordsman-walk-rig.py
The editable .blend, sampled fixed-length pose cycle and diagnostic renders
live separately from painted masters. --directions selects initial QA views.
"""
import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('walk_cycle', ROOT/'tools/swordsman-walk-cycle.py')
cycle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cycle)
parser = argparse.ArgumentParser()
parser.add_argument('--directions', nargs='+', choices=cycle.DIRECTIONS, default=list(cycle.DIRECTIONS))
parser.add_argument('--candidate', default='candidate-01')
parser.add_argument('--cycle-source', type=Path, help='Immutable source snapshot when reproducing a retained candidate')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if args.cycle_source:
    spec = importlib.util.spec_from_file_location('walk_cycle_snapshot', args.cycle_source)
    cycle = importlib.util.module_from_spec(spec); spec.loader.exec_module(cycle)
OUT = ROOT/'authoring/characters/swordsman-production/rig-walk'/args.candidate
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 12
scene.cycles.use_denoising = False
scene.render.resolution_x = scene.render.resolution_y = 320
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True
scene.view_settings.view_transform = 'Standard'
scene.render.fps = 100
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.35, .35, .35, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .7


def mat(name, color):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = 1.
    bsdf.inputs['Specular IOR Level'].default_value = 0.
    return material


materials = {'R': mat('Anatomical right / blue', (.12, .48, .71)),
             'L': mat('Anatomical left / orange', (.82, .37, .12)),
             'neutral': mat('Neutral authoring proxy', (.48, .52, .55)),
             'joint': mat('Joint centres', (.86, .87, .86)),
             'heel': mat('Heel pivot', (.68, .27, .54)),
             'toe': mat('Toe pivot', (.26, .69, .39))}
rest = cycle.pose(.25)['bones']
armature = bpy.data.armatures.new('Fixed-length authoring human chain')
rig = bpy.data.objects.new('Swordsman walk authoring rig / NOT GAME ART', armature)
scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for name, (a, b) in rest.items():
    bone = armature.edit_bones.new(name); bone.head = a; bone.tail = b
    bone.use_deform = True
for side in ('R', 'L'):
    for child, parent, connected in [('femur', 'pelvis', False), ('tibia', side+'-femur', True),
                                    ('foot', side+'-tibia', True), ('upperarm', 'spine', False),
                                    ('forearm', side+'-upperarm', True)]:
        child_name = side+'-'+child
        armature.edit_bones[child_name].parent = armature.edit_bones[parent]
        armature.edit_bones[child_name].use_connect = connected
armature.edit_bones['spine'].parent = armature.edit_bones['pelvis']
armature.edit_bones['neck'].parent = armature.edit_bones['spine']; armature.edit_bones['neck'].use_connect = True
armature.edit_bones['head'].parent = armature.edit_bones['neck']; armature.edit_bones['head'].use_connect = True
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front = True; armature.display_type = 'STICK'
rig['authoring_only'] = True
rig['knee_pole'] = 'Anatomical +Y, never screen-right'
rig['fixed_lengths_metres'] = json.dumps({'femur': cycle.FEMUR, 'tibia': cycle.TIBIA, 'foot': cycle.FOOT_LENGTH})


def bind(obj, bone, material):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.data.materials.append(material)
    group = obj.vertex_groups.new(name=bone)
    group.add(list(range(len(obj.data.vertices))), 1., 'REPLACE')
    modifier = obj.modifiers.new('Authoring armature; offline bake only', 'ARMATURE'); modifier.object = rig
    for poly in obj.data.polygons: poly.use_smooth = True
    obj.select_set(False)


def sphere(name, centre, scale, bone, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=centre)
    obj = bpy.context.object; obj.name = name; obj.scale = scale
    bind(obj, bone, material)


def segment(name, a, b, radius, bone, material):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object; obj.name = name
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    bind(obj, bone, material)


for name, (a, b) in rest.items():
    side = name[0] if name[0] in ('R', 'L') else 'neutral'
    if name.endswith('-foot'): continue
    radius = .052 if name.endswith('femur') else .041 if name.endswith('tibia') else .032 if side != 'neutral' else .045
    segment(name+' fixed-length link', a, b, radius, name, materials[side])
    if side != 'neutral': sphere(name+' joint centre', a, (.052,)*3, name, materials['joint'])
sphere('Blank head; no character identity art', rest['head'][1]+cycle.np.array((0., 0., .02)), (.14, .13, .17), 'head', materials['neutral'])
sphere('Ribcage proxy', (Vector(rest['spine'][0])+Vector(rest['spine'][1]))/2+Vector((0., 0., .08)), (.19, .105, .24), 'spine', materials['neutral'])
sphere('Pelvis proxy', cycle.pose(.25)['pelvis'], (.15, .095, .085), 'pelvis', materials['neutral'])
for side in ('R', 'L'):
    ankle = Vector(rest[side+'-foot'][0])
    f = cycle.pose(.25)['feet'][side]
    # Build the full rigid foot in its rest pose, with heel and toe located
    # from the same ankle transform (no separate toe scaling or sliding).
    points = []
    for x in (-.045, .045):
        for y in (cycle.HEEL, cycle.TOE):
            for z in (-cycle.ANKLE_HEIGHT, -.025):
                pitch = f['pitch']
                points.append(tuple(ankle+Vector((x, y*math.cos(pitch)-z*math.sin(pitch), y*math.sin(pitch)+z*math.cos(pitch)))))
    mesh = bpy.data.meshes.new(side+' rigid heel-to-toe foot')
    mesh.from_pydata(points, [], [(0,1,3,2), (4,6,7,5), (0,4,5,1), (2,3,7,6), (0,2,6,4), (1,5,7,3)])
    obj = bpy.data.objects.new(side+' rigid heel-to-toe foot', mesh); scene.collection.objects.link(obj)
    bind(obj, side+'-foot', materials[side])
    for kind in ('heel', 'toe'):
        sphere(side+' '+kind+' contact pivot', f[kind], (.017,)*3, side+'-foot', materials[kind])
    sphere(side+' ankle joint centre', ankle, (.049,)*3, side+'-foot', materials['joint'])

bpy.ops.object.light_add(type='AREA', location=(-3., 4., 6.))
light = bpy.context.object; light.data.energy = 400; light.data.shape = 'DISK'; light.data.size = 5.
bpy.ops.object.camera_add()
camera = bpy.context.object; scene.camera = camera
camera.data.type = 'ORTHO'; camera.data.ortho_scale = 2.65


def camera_for(direction):
    index = cycle.DIRECTIONS.index(direction)
    azimuth = -index*math.pi/4
    centre = Vector((0., 0., 1.))
    camera.location = centre+Vector((6*math.sin(azimuth), 6*math.cos(azimuth), 6))
    camera.rotation_euler = (centre-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.shift_x = camera.data.shift_y = 0.
    bpy.context.view_layer.update()
    root = world_to_camera_view(scene, camera, Vector((0., 0., 0.)))
    camera.data.shift_x = root.x-.5
    camera.data.shift_y = root.y-(1-264/320)
    bpy.context.view_layer.update()
    registered = world_to_camera_view(scene, camera, Vector((0., 0., 0.)))
    assert abs(registered.x-.5) < 1e-6 and abs(registered.y-.175) < 1e-6, tuple(registered)


evaluated_error = 0.
evaluated_foot_error = 0.
for index in range(113):
    phase = index/112
    p = cycle.pose(phase)
    for name, (a, b) in p['bones'].items():
        bone = rig.pose.bones[name]
        a, b = Vector(a), Vector(b)
        rotation = Vector((0., 1., 0.)).rotation_difference(b-a)
        bone.rotation_mode = 'QUATERNION'
        bone.matrix = Matrix.Translation(a)@rotation.to_matrix().to_4x4()
        bpy.context.view_layer.update()
        for property_name in ('location', 'rotation_quaternion', 'scale'):
            bone.keyframe_insert(property_name, frame=index+1)
    bpy.context.view_layer.update()
    for name, (a, b) in p['bones'].items():
        actual = rig.pose.bones[name]
        error = max((actual.head-Vector(a)).length, (actual.tail-Vector(b)).length)
        evaluated_error = max(evaluated_error, error)
        assert error < 1e-5, (index, name, error)
        assert all(abs(v-1.) < 1e-5 for v in actual.scale), (index, name, tuple(actual.scale))
    for side in ('R', 'L'):
        bone = rig.pose.bones[side+'-foot']
        transform = bone.matrix@armature.bones[bone.name].matrix_local.inverted()
        for kind in ('heel', 'toe'):
            actual = transform@Vector(cycle.pose(.25)['feet'][side][kind])
            error = (actual-Vector(p['feet'][side][kind])).length
            evaluated_foot_error = max(evaluated_foot_error, error)
            assert error < 1e-5, (index, side, kind, error)
for action in bpy.data.actions:
    for curve in action.fcurves:
        for key in curve.keyframe_points: key.interpolation = 'LINEAR'
scene.frame_start = 1; scene.frame_end = 112
scene['status'] = 'RIG_ONLY / AWAITING_VISUAL_GATE / NOT_OWNER_APPROVED'
scene['cycle_seconds'] = cycle.CYCLE_SECONDS
scene['cycle_distance_metres'] = cycle.CYCLE_DISTANCE
camera_for('S'); scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'walk-proof.blend'), compress=True)
manifest = {'status': 'AWAITING_RIG_VISUAL_GATE', 'authoringOnly': True, 'paintedLayersApplied': False,
            'directions': list(cycle.DIRECTIONS), 'canvas': [320,320], 'root': [160,264],
            'cameraElevationDegrees': 45, 'cycleSeconds': cycle.CYCLE_SECONDS,
            'cycleDistance': cycle.CYCLE_DISTANCE, 'stanceFraction': cycle.DUTY,
            'lengthsMetres': {'femur': cycle.FEMUR, 'tibia': cycle.TIBIA, 'foot': cycle.FOOT_LENGTH},
            'maxEvaluatedBlenderJointErrorMetres': evaluated_error,
            'maxEvaluatedBlenderHeelToeErrorMetres': evaluated_foot_error,
            'phaseNames': list(cycle.PHASE_NAMES),
            'poses': [cycle.serializable(cycle.pose(i/8)) for i in range(8)]}
manifest['projections'] = {}
for direction in cycle.DIRECTIONS:
    camera_for(direction)
    def project(point):
        v = world_to_camera_view(scene, camera, Vector(point))
        return [v.x*320, (1-v.y)*320]
    manifest['projections'][direction] = [
        {'root': project(p['root']), 'pelvis': project(p['pelvis']),
         'feet': {side: {name: project(f[name]) for name in ('hip','knee','ankle','heel','sole','toe')}
                  for side, f in p['feet'].items()}}
        for p in [cycle.pose(i/8) for i in range(8)]]
camera_for('S')
(OUT/'shared-cycle.json').write_text(json.dumps(manifest, indent=2)+'\n')
for direction in args.directions:
    camera_for(direction)
    for i in range(8):
        scene.frame_set(1+i*14)
        scene.render.filepath = str(OUT/f'{direction}-{i}.png')
        bpy.ops.render.render(write_still=True)
    print('Rendered articulated authoring proof:', direction, flush=True)
print('Fixed lengths and actual evaluated Blender joints passed; visual gate pending.', evaluated_error, flush=True)
