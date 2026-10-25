"""Render a separate native-motion to Astraeon canonical-rig pilot.

Blender 5.2 only. Existing patch captures, source rig and final artwork are not
modified. Outputs are clothed 3D painting guides, never final sprite art.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion, Vector


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


MAP = {'Hips': 'pelvis', 'Spine': 'spine_01', 'Chest': 'spine_03',
       'Neck': 'neck_01', 'Head': 'head'}
for side, suffix in [('R', 'r'), ('L', 'l')]:
    for target, donor in [('Clavicle', 'clavicle'), ('UpperArm', 'upperarm'),
                          ('Forearm', 'lowerarm'), ('Hand', 'hand'),
                          ('Thigh', 'thigh'), ('Shin', 'calf'),
                          ('Foot', 'foot'), ('Toe', 'ball')]:
        MAP[target + '.' + side] = donor + '_' + suffix
    for digit in ['Index', 'Middle', 'Ring', 'Pinky', 'Thumb']:
        for index in range(1, 4):
            MAP[f'{digit}{index}.{side}'] = f'{digit.lower()}_{index:02d}_{suffix}'
YAWS = {'S': 0, 'SW': -45, 'W': -90, 'NW': -135,
        'N': 180, 'NE': 135, 'E': 90, 'SE': 45}
ATTACK_DIRECTIONS = ['SW','NW','NE','SE']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skeleton', type=Path, required=True)
    parser.add_argument('--rig', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--directions', nargs='+', default=ATTACK_DIRECTIONS)
    parser.add_argument('--resolution', type=int, default=1536)
    parser.add_argument('--weapon', choices=['staff', 'bow'], default='staff')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if len(set(args.directions))!=len(args.directions) or not set(args.directions).issubset(YAWS):
        raise ValueError('Choose unique real canonical camera directions')
    if bpy.app.version[:2] != (5, 2):
        raise ValueError('Canonical rig requires Blender 5.2')
    if args.output.exists():
        raise ValueError('Choose a new pilot destination')
    donor = json.loads(args.skeleton.read_text())
    if donor['status'] != 'EVALUATED_SOURCE_SKELETON_METADATA_NOT_NEW_IMAGE_CAPTURE':
        raise ValueError('Expected checked native skeleton metadata')
    rig_sha = sha(args.rig)
    bpy.ops.wm.open_mainfile(filepath=str(args.rig.resolve()))
    if len(bpy.data.actions):
        raise ValueError('Canonical source unexpectedly contains old animation actions')
    scene = bpy.context.scene
    rig = bpy.data.objects['ARM_FantasyCharacter01']
    root = bpy.data.objects['ROOT_FantasyCharacter01']
    base_ortho = scene.camera.data.ortho_scale
    # One actor scale from the original fixed camera, never per-frame fitting.
    actor_scale = 3.55 / base_ortho
    root.scale = (actor_scale,) * 3
    root.rotation_euler = (0, 0, 0)
    for obj in scene.objects:
        if obj.type == 'MESH':
            obj.hide_render = obj.name not in ['F01_BodyOutfit', 'F01_HeadHair']
    rig.animation_data_clear()
    for bone in rig.pose.bones:
        for constraint in bone.constraints:
            constraint.influence = 0
    rest = {name: Matrix(data['world_matrix']) for name, data in donor['rest_bones'].items()}
    target_rest = {bone.name: bone.matrix_local.copy() for bone in rig.data.bones}
    source_hip = rest['pelvis'].translation
    source_leg = source_hip.z - rest['foot_r'].translation.z
    target_leg = target_rest['Hips'].translation.z - target_rest['Foot.R'].translation.z
    leg_scale = target_leg / source_leg
    camera = scene.camera
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 5.325
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    scene.display.render_aa = 'OFF'
    shade = scene.display.shading
    shade.light = 'STUDIO'
    shade.color_type = 'MATERIAL'
    shade.show_cavity = True
    shade.show_shadows = True
    scene.render.image_settings.color_depth = '8'
    # Staff is attached to the actual target palm. Its local axis is calibrated
    # once from the first native held-staff sample, not from image coordinates.
    data = bpy.data.curves.new('PilotGuideStaff', 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = .020
    data.bevel_resolution = 2
    staff = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(staff)
    material = bpy.data.materials.new('PilotStaffWood')
    material.diffuse_color = (.30, .15, .06, 1)
    data.materials.append(material)
    prop_curves = {}
    if args.weapon == 'bow':
        staff.hide_render = True
        for name, radius, color in [('bow', .018, (.30, .15, .06, 1)),
                                    ('string', .003, (.8, .8, .75, 1)),
                                    ('arrow', .006, (.55, .40, .15, 1))]:
            curve = bpy.data.curves.new('Pilot_' + name, 'CURVE')
            curve.dimensions = '3D'
            curve.bevel_depth = radius
            obj = bpy.data.objects.new(curve.name, curve)
            scene.collection.objects.link(obj)
            mat = bpy.data.materials.new(curve.name + '_material')
            mat.diffuse_color = color
            curve.materials.append(mat)
            prop_curves[name] = obj
    staff_local_axis = None

    def pose(frame):
        nonlocal staff_local_axis
        for bone in rig.pose.bones:
            bone.matrix_basis = Matrix.Identity(4)
            bone.rotation_mode = 'QUATERNION'
        desired = {target: Matrix(frame['bones'][source]['world_matrix']).to_quaternion()
                   @ rest[source].to_quaternion().inverted()
                   @ target_rest[target].to_quaternion() for target, source in MAP.items()}
        for bone in sorted(rig.pose.bones, key=lambda b: len(b.parent_recursive)):
            if bone.name not in desired:
                continue
            inherited = target_rest[bone.name].to_quaternion()
            if bone.parent:
                parent = bone.parent.name
                parent_pose = desired.get(parent, target_rest[parent].to_quaternion())
                inherited = parent_pose @ target_rest[parent].to_quaternion().inverted() @ inherited
            bone.rotation_quaternion = inherited.inverted() @ desired[bone.name]
        displacement = (Vector(frame['bones']['pelvis']['head']) - source_hip) * leg_scale
        rig.pose.bones['Hips'].location = target_rest['Hips'].to_3x3().inverted() @ displacement
        # Fingers use the same explicit native world-rest transfer as the arms.
        # No old action or hand-authored wrist twist is restored from the rig.
        bpy.context.view_layer.update()
        rotation_errors = {}
        for name, expected in desired.items():
            actual = rig.pose.bones[name].matrix.to_quaternion()
            angle = actual.rotation_difference(expected).angle
            rotation_errors[name] = min(angle, abs(2 * math.pi - angle))
        if max(rotation_errors.values()) > 1e-3:
            raise ValueError('Target world-rest rotation transfer differs: ' + json.dumps(rotation_errors))
        body = bpy.data.objects['F01_BodyOutfit']
        evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        floor = min((evaluated.matrix_world @ vertex.co).z for vertex in mesh.vertices)
        evaluated.to_mesh_clear()
        # Floor correction is one 3D pelvis translation, shared by every view.
        matrix = rig.matrix_world @ rig.pose.bones['Hips'].matrix
        matrix.translation.z -= floor
        rig.pose.bones['Hips'].matrix = rig.matrix_world.inverted() @ matrix
        bpy.context.view_layer.update()
        evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        corrected_floor = min((evaluated.matrix_world @ vertex.co).z for vertex in mesh.vertices)
        evaluated.to_mesh_clear()
        if abs(corrected_floor) > 2e-5:
            raise ValueError('Canonical pilot body does not contact the floor')
        palm = sum((rig.matrix_world @ rig.pose.bones[name + '1.R'].head
                    for name in ['Index', 'Pinky']), Vector()) * .5
        hand_rotation = (rig.matrix_world @ rig.pose.bones['Hand.R'].matrix).to_quaternion()
        if staff_local_axis is None:
            staff_local_axis = hand_rotation.inverted() @ Vector((0, 0, 1))
        axis = hand_rotation @ staff_local_axis
        data.splines.clear()
        spline = data.splines.new('POLY')
        spline.points.add(1)
        for point, value in zip(spline.points, [palm - axis * .82, palm + axis * .76]):
            point.co = (*value, 1)
        bow_diagnostics = {}
        if args.weapon == 'bow':
            left = sum((rig.matrix_world @ rig.pose.bones[name + '1.L'].head
                        for name in ['Index', 'Pinky']), Vector()) * .5
            aim = left - palm
            if aim.length < .02:
                raise ValueError('Degenerate bow draw direction')
            aim.normalize()
            up = Vector((0, 0, 1))
            up -= aim * up.dot(aim)
            up.normalize()
            ends = [left + up * (.52 * t) + aim * (-.22 * t * t + .07 * abs(t) ** 6)
                    for t in [k / 12 - 1 for k in range(25)]]
            draw = frame.get('source_weapon_guide', {}).get('arrow_visible')
            if draw is None:
                draw = 'Draw' in frame['action'] or ('Release' in frame['action'] and frame['source_frame'] < 10)
            nock = palm if draw else left - aim * .15
            for name, values in [('bow', ends), ('string', [ends[0], nock, ends[-1]]),
                                 ('arrow', [nock, left + aim * .4])]:
                curve = prop_curves[name].data
                curve.splines.clear()
                line = curve.splines.new('POLY')
                line.points.add(len(values) - 1)
                for point, value in zip(line.points, values):
                    point.co = (*value, 1)
            prop_curves['arrow'].hide_render = not draw
            bow_diagnostics = {'bow_grip_world': list(left), 'string_nock_world': list(nock),
                               'arrow_visible': draw, 'bow_attached_to_palm': True,
                               'cheek_contact_review_required': True}
        return {'floor_correction_m': -floor, 'corrected_floor_m': corrected_floor,
                'maximum_world_rotation_error_rad': max(rotation_errors.values()),
                'grip_world': list(palm),
                'staff_tip_world': list(palm + axis * .76), **bow_diagnostics}

    args.output.mkdir(parents=True)
    (args.output / 'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    views = {}
    for direction in args.directions:
        radians = math.radians(YAWS[direction])
        offset = Vector((6 * math.sin(radians), -6 * math.cos(radians), 3.1))
        camera.rotation_euler = (-offset).to_track_quat('-Z', 'Y').to_euler()
        up = camera.rotation_euler.to_matrix() @ Vector((0, 1, 0))
        camera.location = up * 1.15375 + offset
        folder = args.output / direction
        folder.mkdir()
        rows = []
        for frame in donor['frames']:
            diagnostics = pose(frame)
            def project(point):
                value = world_to_camera_view(scene, camera, point)
                return [value.x * args.resolution, (1 - value.y) * args.resolution]
            landmarks = {name: project(rig.matrix_world @ rig.pose.bones[name].head)
                         for name in MAP}
            path = folder / f"{frame['index']:03d}.png"
            scene.render.filepath = str(path.resolve())
            bpy.ops.render.render(write_still=True)
            rows.append({'index': frame['index'], 'source_action': frame['action'],
                         'source_frame': frame['source_frame'], 'landmarks': landmarks,
                         **diagnostics, 'image_sha256': sha(path)})
        views[direction] = {'camera': {'location': list(camera.location),
                            'rotation': list(camera.rotation_euler),
                            'ortho_scale': camera.data.ortho_scale}, 'frames': rows}
    if sha(args.rig) != rig_sha:
        raise ValueError('Canonical source changed')
    receipt = {'status': 'CANONICAL_RIG_RETARGET_PILOT_GUIDE_NOT_FINAL_ART',
               'source_skeleton_sha256': sha(args.skeleton), 'rig_sha256': rig_sha,
               'implementation_sha256': sha(__file__), 'blender': bpy.app.version_string,
               'actor_scale': actor_scale, 'leg_scale': leg_scale, 'bone_map': MAP,
               'weapon': args.weapon,
               'views': views, 'old_actions_used': False, 'source_modified': False,
               'runtime_admitted': False, 'needs_anatomy_and_prop_contact_review': True}
    (args.output / 'pilot-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
