"""Blender offline cutout-rig renderer. Run with blender -b --python ... -- args.

Image cards are independent painted attachments bound rigidly to real edit bones.
The same canonical body-space timeline is projected for each exact named heading.
No geometry placeholders or historical rejected character images are inputs.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from painted_character_factory import (PARENTS, SLOTS, attachment_points,
                                       read_spec, require_coverage, sample_pose,
                                       variant_enabled)


def stage_point(point):
    return Vector((point[0], 320-point[1], 0))


def bone_matrix(points, rest_length):
    start, end = map(stage_point, points)
    delta = end-start
    length = delta.length
    if length < 0.01:
        raise ValueError('Projected bone has zero length; view needs a pose substitution')
    y = delta.normalized()
    x = Vector((y.y, -y.x, 0))
    matrix = Matrix(((x.x, y.x*length/rest_length, 0, start.x),
                     (x.y, y.y*length/rest_length, 0, start.y),
                     (0, 0, 1, 0), (0, 0, 0, 1)))
    return matrix


def make_material(image, name, holdout=False):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.interpolation = 'Linear'
    tex.extension = 'CLIP'
    emission = nodes.new('ShaderNodeHoldout' if holdout else 'ShaderNodeEmission')
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader')
    output = nodes.new('ShaderNodeOutputMaterial')
    links = material.node_tree.links
    if not holdout:
        links.new(tex.outputs['Color'], emission.inputs['Color'])
    links.new(tex.outputs['Alpha'], mix.inputs[0])
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(emission.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs['Surface'])
    return material


def setup_scene(spec, folder, direction):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 1
    scene.cycles.use_denoising = False
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
    scene.cycles.transparent_max_bounces = 64
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = 320
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.render.filter_size = 0.5
    scene.render.use_stamp = False
    scene.render.use_stamp_date = False
    scene.render.use_stamp_time = False
    scene.render.use_stamp_frame = False
    scene.render.use_stamp_filename = False
    scene.render.use_stamp_render_time = False
    camera_data = bpy.data.cameras.new('FixedCanvasCamera')
    camera = bpy.data.objects.new('FixedCanvasCamera', camera_data)
    scene.collection.objects.link(camera)
    camera.location = (160, 160, 1000)
    camera.rotation_euler = (0, 0, 0)
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 320
    scene.camera = camera
    scene['projection'] = 'fixed body-world 30deg elevation; exact heading; 320 RGBA root 160,264'
    scene['owner_approval'] = 'DEV_ONLY / REQUIRED'
    scene['source_sha256'] = spec['images']['SE']['sha256']
    rest = sample_pose(spec, direction, 'Idle', 0)
    armature = bpy.data.armatures.new('PaintedCharacterRig')
    rig = bpy.data.objects.new('PaintedCharacterRig', armature)
    scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, parent in PARENTS.items():
        bone = armature.edit_bones.new(name)
        bone.head, bone.tail = map(stage_point, rest['bones'][name])
        bone.roll = 0
        if parent:
            bone.parent = armature.edit_bones[parent]
        bone.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.show_in_front = True
    images = {name: bpy.data.images.load(str((folder/source['file']).resolve()), check_existing=True)
              for name, source in spec['images'].items()}
    for image in images.values():
        image.colorspace_settings.name = 'sRGB'
        image.pack()
    cards = []
    for attachment in spec['views'][direction]['attachments']:
        bone = armature.bones[attachment['bone']]
        vertices = [bone.matrix_local @ Vector(v) for v in attachment_points(attachment)]
        mesh = bpy.data.meshes.new(attachment['id'])
        mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
        uv = mesh.uv_layers.new(name='SourceAtlas')
        x, y, w, h = attachment['rect']
        iw, ih = spec['images'][attachment['image']]['size']
        coords = [(x/iw, 1-(y+h)/ih), ((x+w)/iw, 1-(y+h)/ih),
                  ((x+w)/iw, 1-y/ih), (x/iw, 1-y/ih)]
        for loop, coord in zip(uv.data, coords):
            loop.uv = coord
        card = bpy.data.objects.new(attachment['id'], mesh)
        scene.collection.objects.link(card)
        group = card.vertex_groups.new(name=attachment['bone'])
        group.add(range(4), 1.0, 'REPLACE')
        modifier = card.modifiers.new('RigidPaintedPartBinding', 'ARMATURE')
        modifier.object = rig
        material = make_material(images[attachment['image']], attachment['id'])
        card.data.materials.append(material)
        card.data.materials.append(make_material(images[attachment['image']], attachment['id']+'-grip-holdout', holdout=True))
        card['slot'] = attachment['slot']
        card['attachment'] = json.dumps(attachment)
        card['select'] = json.dumps(attachment.get('select', {}))
        cards.append((attachment, card))
    lengths = {name: armature.bones[name].length for name in PARENTS}
    return scene, rig, cards, lengths


def apply_pose(rig, pose, lengths, frame=None):
    # Parent-first updates preserve desired absolute matrices in hierarchical bones.
    for name in PARENTS:
        bone = rig.pose.bones[name]
        bone.rotation_mode = 'QUATERNION'
        bone.matrix = bone_matrix(pose['bones'][name], lengths[name])
        bpy.context.view_layer.update()
        if frame is not None:
            bone.keyframe_insert('location', frame=frame)
            bone.keyframe_insert('rotation_quaternion', frame=frame)
            bone.keyframe_insert('scale', frame=frame)


def render(scene, cards, variant, path, slot=None):
    for attachment, card in cards:
        is_grip_mask = (slot == 'Weapon' and attachment['bone'] == 'hand_R' and
                       attachment['slot'] == ('BodyHands' if variant['outfit'] == 'none' else 'Hands'))
        card.data.polygons[0].material_index = 1 if is_grip_mask else 0
        card.hide_render = (not variant_enabled(attachment, variant) or
                            (slot is not None and attachment['slot'] != slot and not is_grip_mask))
    scene.render.filepath = str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--directions', default='SE')
    parser.add_argument('--actions', default='Idle,Walk,BasicAttack')
    parser.add_argument('--indices', help='Optional explicit pose indices for a fitting proof')
    parser.add_argument('--composite-only', action='store_true')
    parser.add_argument('--variants', default='default')
    parser.add_argument('--save-rig', action='store_true')
    argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    args = parser.parse_args(argv)
    spec = read_spec(args.spec)
    directions, actions = args.directions.split(','), args.actions.split(',')
    require_coverage(spec, directions, actions)
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = {'status': 'DEV_ONLY_PILOT_NOT_APPROVED', 'blenderVersion': bpy.app.version_string,
               'specSHA256': hashlib.sha256(args.spec.read_bytes()).hexdigest(),
               'motionControllerSHA256': hashlib.sha256((Path(__file__).parent/'painted_character_factory.py').read_bytes()).hexdigest(),
               'rendererSHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'directions': directions, 'actions': actions, 'poses': [],
               'registration': spec['registration'], 'mirroring': 'none', 'outputs': []}
    for direction in directions:
        scene, rig, cards, lengths = setup_scene(spec, args.spec.resolve().parent, direction)
        for action in actions:
            clip = spec['motions'][action]
            indices = list(map(int, args.indices.split(','))) if args.indices else range(len(clip['durations']))
            animation = bpy.data.actions.new(direction+'_'+action)
            rig.animation_data_create()
            rig.animation_data.action = animation
            for index in indices:
                scene.frame_set(index+1)
                pose = sample_pose(spec, direction, action, index)
                apply_pose(rig, pose, lengths, frame=index+1)
                receipt['poses'].append({**pose, 'duration': clip['durations'][index]})
                for variant_name in args.variants.split(','):
                    variant = spec['variants'][variant_name]
                    if args.composite_only:
                        targets = [('Composite', None)]
                    else:
                        targets = [(slot, slot) for slot in SLOTS] + [('Composite', None)]
                    for label, slot in targets:
                        path = args.output/variant_name/action/direction/label/f'{index:02}.png'
                        render(scene, cards, variant, path, slot)
                        receipt['outputs'].append({'file': path.relative_to(args.output).as_posix(),
                                                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            animation.use_fake_user = True
        if args.save_rig:
            rig.animation_data.action = bpy.data.actions.get(direction+'_Idle')
            scene.frame_set(1)
            scene.frame_start = 1
            scene.frame_end = max(len(spec['motions'][a]['durations']) for a in actions)
            for attachment, card in cards:
                card.hide_render = not variant_enabled(attachment, spec['variants']['default'])
            bpy.ops.wm.save_as_mainfile(filepath=str(args.output/(direction+'-painted-rig.blend')))
    (args.output/'render-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print('PAINTED_FACTORY_RECEIPT', args.output/'render-receipt.json')


if __name__ == '__main__':
    main()
