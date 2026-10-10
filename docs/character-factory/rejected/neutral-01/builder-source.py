"""Authoring-only Blender rig and fixed-camera guide factory.

Run with Blender --background --factory-startup --python this-file -- --output PATH.
Use --scene to render an edited canonical .blend instead of rebuilding it.
No painted input is sampled; no runtime assets or gameplay code are written.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'tools/swordsman-walk-cycle.py').exists())
DEFAULT_CONFIG = ROOT / 'authoring/characters/swordsman-production/factory/canonical/definition.json'


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def rounded(value):
    return [round(float(v), 6) for v in value]


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = 1
    bsdf.inputs['Specular IOR Level'].default_value = 0
    return mat


def build(cfg):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    data = bpy.data.armatures.new('ASTRAEON_CANONICAL_SKELETON')
    rig = bpy.data.objects.new('ASTRAEON_RIG', data)
    scene.collection.objects.link(rig)
    root = bpy.data.objects.new('ASTRAEON_CHARACTER_ROOT', None)
    scene.collection.objects.link(root)
    rig.parent = root
    root['authoring_only'] = True
    root['direction_rotation_only'] = True
    rig['identity_fit'] = cfg['identityFit']
    rig['anatomical_axes'] = cfg['coordinateSystem']
    spec = importlib.util.spec_from_file_location('original_walk_ik', ROOT / 'tools/swordsman-walk-cycle.py')
    motion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(motion)
    r = cfg['rig']
    hip = Vector((0, 0, r['hipHeight']))
    chest = hip + Vector((0, .018, r['chestAboveHip']))
    neck = hip + Vector((0, .024, r['neckAboveHip']))
    head = hip + Vector((0, .024, r['headAboveHip']))
    bones = {'root': ((0, 0, 0), (0, 0, .12), None),
             'pelvis': (hip, hip + Vector((0, 0, .12)), 'root'),
             'spine': (hip, chest, 'pelvis'),
             'neck': (chest, neck, 'spine'), 'head': (neck, head, 'neck')}
    sockets = {'root': Vector((0, 0, 0)), 'head': head,
               'back': chest + Vector((0, -.12, 0)), 'waist': hip}
    for side, sign in [('R', 1), ('L', -1)]:
        h = hip + Vector((sign * r['hipHalfWidth'], 0, 0))
        ankle = Vector((sign * r['hipHalfWidth'], 0, r['ankleHeight']))
        knee = Vector(motion.ik(h, ankle, r['femur'], r['tibia']))
        shoulder = chest + Vector((sign * r['shoulderHalfWidth'], 0, 0))
        hand = hip + Vector((sign * .235, .05, .015))
        elbow = Vector(motion.ik(shoulder, hand, r['upperarm'], r['forearm']))
        bones[side + '-femur'] = (h, knee, 'pelvis')
        bones[side + '-tibia'] = (knee, ankle, side + '-femur')
        bones[side + '-foot'] = (ankle, ankle + Vector((0, r['footLength'], 0)), side + '-tibia')
        bones[side + '-upperarm'] = (shoulder, elbow, 'spine')
        bones[side + '-forearm'] = (elbow, hand, side + '-upperarm')
        sockets['hand_' + side] = hand
        sockets['foot_' + side] = ankle - Vector((0, 0, r['ankleHeight']))
    parents = {'head': 'head', 'back': 'spine', 'waist': 'pelvis',
               'hand_R': 'R-forearm', 'hand_L': 'L-forearm',
               'foot_R': 'R-foot', 'foot_L': 'L-foot'}
    for name, point in sockets.items():
        if name != 'root':
            bones[cfg['sockets'][name]] = (point, point + Vector((0, 0, .04)), parents[name])
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, (a, b, parent) in bones.items():
        bone = data.edit_bones.new(name)
        bone.head, bone.tail = a, b
        if parent:
            bone.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.show_in_front = True
    data.display_type = 'STICK'
    # One neutral guide key only. Nine Golden actions remain pending.
    rig.animation_data_create()
    rig.animation_data.action = bpy.data.actions.new('FactoryNeutral')
    for bone in rig.pose.bones:
        bone.rotation_mode = 'QUATERNION'
        for prop in ('location', 'rotation_quaternion', 'scale'):
            bone.keyframe_insert(prop, frame=1)
    mats = {'R': material('Anatomical right / BLUE', (.10, .43, .75)),
            'L': material('Anatomical left / ORANGE', (.90, .32, .09)),
            'neutral': material('Unpainted proxy', (.48, .55, .60)),
            'Hair': material('Hair attachment guide', (.50, .40, .72)),
            'Outfit': material('Outfit fit guide', (.14, .60, .48)),
            'Weapon': material('Right-hand blade guide', (.24, .64, .89)),
            'Headgear': material('Headgear attachment guide', (.89, .71, .23)),
            'BackAccessory': material('Back attachment guide', (.59, .24, .40))}
    collections = {}
    for name in cfg['layers']:
        coll = bpy.data.collections.new(name)
        scene.collection.children.link(coll)
        coll['purpose'] = 'Structural guide; NOT painted final artwork'
        collections[name] = coll

    def bind(obj, name, bone, layer, mat):
        obj.name = name
        for coll in list(obj.users_collection):
            coll.objects.unlink(obj)
        collections[layer].objects.link(obj)
        # Geometry starts in canonical rig coordinates. Apply exactly once.
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.data.materials.append(mat)
        obj.parent = root
        group = obj.vertex_groups.new(name=bone)
        group.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
        modifier = obj.modifiers.new('Canonical authoring rig', 'ARMATURE')
        modifier.object = rig
        obj['logical_layer'] = layer
        obj['attachment_bone'] = bone
        obj['guide_only'] = True
        for poly in obj.data.polygons:
            poly.use_smooth = True
        obj.select_set(False)

    def sphere(name, centre, scale, bone, layer, mat):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=centre)
        obj = bpy.context.object
        obj.scale = scale
        bind(obj, name, bone, layer, mat)

    def box(name, centre, scale, bone, layer, mat):
        bpy.ops.mesh.primitive_cube_add(size=2, location=centre)
        obj = bpy.context.object
        obj.scale = scale
        bind(obj, name, bone, layer, mat)

    proxy = cfg['proxy']
    for name, (a, b, _) in bones.items():
        if name == 'root' or name.startswith('socket_') or name.endswith('-foot'):
            continue
        a, b = Vector(a), Vector(b)
        side = name[0] if name[0] in ('R', 'L') else 'neutral'
        radius = proxy['thighRadius'] if name.endswith('femur') else proxy['shinRadius'] if name.endswith('tibia') else proxy['armRadius'] if side != 'neutral' else .045
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=(b-a).length, location=(a+b)/2)
        obj = bpy.context.object
        obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
        bind(obj, name + ' link', name, 'BaseBody', mats[side])
        if side != 'neutral':
            sphere(name + ' joint', a, (.054,) * 3, name, 'BaseBody', mats[side])
    sphere('Head proxy / NO FACE IDENTITY', head + Vector((0, 0, .02)), proxy['headRadii'], 'head', 'BaseBody', mats['neutral'])
    sphere('Chest proxy', (hip + chest)/2 + Vector((0, 0, .08)), proxy['chestRadii'], 'spine', 'BaseBody', mats['neutral'])
    sphere('Pelvis proxy', hip, proxy['pelvisRadii'], 'pelvis', 'BaseBody', mats['neutral'])
    # Nose/forward marker disambiguates front/back without copying character art.
    sphere('Anatomical forward marker', head + Vector((0, .15, -.015)), (.035, .055, .035), 'head', 'BaseBody', mats['neutral'])
    for side in ('R', 'L'):
        point = sockets['foot_' + side]
        box(side + ' planted rigid foot', point + Vector((0, .05, .035)), (.052, r['footLength']/2, .035), side + '-foot', 'BaseBody', mats[side])
        sphere(side + ' hand', sockets['hand_' + side], (.052,) * 3, cfg['sockets']['hand_' + side], 'BaseBody', mats[side])
    # Abstract attachment markers, not costumes or completed equipment proof.
    sphere('Hair volume marker', head + Vector((0, -.015, .12)), (.17, .155, .10), 'socket_head', 'Hair', mats['Hair'])
    box('Torso outfit clearance marker', (hip + chest)/2 + Vector((0, 0, .08)), (.21, .125, .23), 'spine', 'Outfit', mats['Outfit'])
    box('Right-hand sword guide', sockets['hand_R'] + Vector((0, .015, -.36)), (.018, .012, .34), 'socket_hand_R', 'Weapon', mats['Weapon'])
    box('Sword grip crossbar', sockets['hand_R'] + Vector((0, .015, -.04)), (.10, .018, .015), 'socket_hand_R', 'Weapon', mats['Headgear'])
    sphere('Left-hand offhand mount marker', sockets['hand_L'] + Vector((0, .055, 0)), (.09, .025, .13), 'socket_hand_L', 'Offhand', mats['L'])
    box('Headgear socket marker', head + Vector((0, -.05, .23)), (.10, .055, .025), 'socket_head', 'Headgear', mats['Headgear'])
    box('Back socket marker', sockets['back'] + Vector((0, -.025, -.09)), (.12, .035, .14), 'socket_back', 'BackAccessory', mats['BackAccessory'])
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = 'ASTRAEON_SPRITE_CAMERA'
    c = cfg['camera']
    centre = Vector(c['target'])
    pitch = math.radians(c['elevationDegrees'])
    camera.location = centre + Vector((0, c['distance'] * math.cos(pitch), c['distance'] * math.sin(pitch)))
    camera.rotation_euler = (centre - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = c['projection']
    camera.data.ortho_scale = c['orthographicSpan']
    scene.camera = camera
    scene.render.resolution_x = cfg['canvas']['width']
    scene.render.resolution_y = cfg['canvas']['height']
    scene.render.resolution_percentage = 100
    bpy.context.view_layer.update()
    projected = world_to_camera_view(scene, camera, Vector((0, 0, 0)))
    camera.data.shift_x = projected.x - cfg['canvas']['root'][0] / cfg['canvas']['width']
    camera.data.shift_y = projected.y - (1 - cfg['canvas']['root'][1] / cfg['canvas']['height'])
    for name, position, energy in [('Key', (-3, 4, 6), 450), ('Fill', (3, 1, 3), 100)]:
        bpy.ops.object.light_add(type='AREA', location=position)
        obj = bpy.context.object
        obj.name = 'Guide ' + name
        obj.rotation_euler = (-obj.location).to_track_quat('-Z', 'Y').to_euler()
        obj.data.energy = energy
        obj.data.size = 5
    scene.world = bpy.data.worlds.new('Fixed guide world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.35, .35, .35, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
    scene['factory_status'] = cfg['status']
    scene['factory_config'] = json.dumps(cfg)
    return scene


def render(cfg, scene, output):
    # Saved editable scenes still have to match the frozen view contract.
    if (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage) != (320, 320, 100):
        raise ValueError('Saved scene canvas drift')
    if scene.camera.data.type != 'ORTHO' or abs(scene.camera.data.ortho_scale - cfg['camera']['orthographicSpan']) > 1e-6:
        raise ValueError('Saved scene projection drift')
    render_cfg = cfg['render']
    scene.render.engine = render_cfg['engine']
    scene.cycles.device = render_cfg['device']
    scene.cycles.samples = render_cfg['samples']
    scene.cycles.seed = render_cfg['seed']
    scene.cycles.use_animated_seed = False
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = render_cfg['threads']
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.frame_set(cfg['guideAction']['sourceFrame'])
    root = bpy.data.objects['ASTRAEON_CHARACTER_ROOT']
    rig = bpy.data.objects['ASTRAEON_RIG']
    camera = scene.camera
    offset = camera.location - Vector(cfg['camera']['target'])
    actual_pitch = math.degrees(math.atan2(offset.z, math.hypot(offset.x, offset.y)))
    if abs(actual_pitch - cfg['camera']['elevationDegrees']) > 1e-4 or abs(offset.x) > 1e-6:
        raise ValueError('Saved scene camera elevation/azimuth drift')
    camera_matrix = [rounded(row) for row in camera.matrix_world]
    records = []
    for index, direction in enumerate(cfg['directions']):
        yaw = cfg['camera']['yawOffsetDegrees'] + cfg['camera']['yawSign'] * index * 45
        root.rotation_euler[2] = math.radians(yaw)
        bpy.context.view_layer.update()
        sockets, transforms = {}, {}
        for name, bone_name in cfg['sockets'].items():
            bone = rig.pose.bones[bone_name]
            world = rig.matrix_world @ bone.head
            point = world_to_camera_view(scene, camera, world)
            sockets[name] = [round(point.x * 320, 4), round((1 - point.y) * 320, 4)]
            matrix = rig.matrix_world @ bone.matrix
            transforms[name] = {'bone': bone_name, 'worldPosition': rounded(world),
                                'worldMatrix': [rounded(row) for row in matrix]}
        if max(abs(a-b) for a, b in zip(sockets['root'], cfg['canvas']['root'])) > .0001:
            raise ValueError(('Projected ground root moved', direction, sockets['root']))
        if [rounded(row) for row in camera.matrix_world] != camera_matrix:
            raise ValueError('Camera moved during directional rendering')
        geometry = {}
        for obj in sorted((o for o in scene.objects if o.type == 'MESH'), key=lambda o: o.name):
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            mesh = evaluated.to_mesh()
            coords = [rounded(evaluated.matrix_world @ vertex.co) for vertex in mesh.vertices]
            geometry[obj.name] = hashlib.sha256(json.dumps(coords).encode()).hexdigest()
            evaluated.to_mesh_clear()
        for layer in ['Composite'] + cfg['layers']:
            for name in cfg['layers']:
                # Neutral body/attachments composite; inspect all other guides separately.
                bpy.data.collections[name].hide_render = name not in (['BaseBody', 'Weapon', 'Offhand'] if layer == 'Composite' else [layer])
            target = output / 'Neutral' / direction / layer / 'frame_000.png'
            target.parent.mkdir(parents=True, exist_ok=True)
            scene.render.filepath = str(target.resolve())
            bpy.ops.render.render(write_still=True)
        records.append({'action': 'Neutral', 'direction': direction, 'frameIndex': 0,
                        'sourceFrame': 1, 'durationMs': cfg['guideAction']['durationMs'],
                        'root': sockets['root'], 'sockets': sockets,
                        'attachmentTransforms': transforms, 'yawDegrees': yaw,
                        'geometryHashes': geometry})
        print('FACTORY_DIRECTION_COMPLETE', direction, flush=True)
    for name in cfg['layers']:
        bpy.data.collections[name].hide_render = False
    root.rotation_euler[2] = 0
    dump(output / 'render-metadata.json', {
        'status': cfg['status'], 'authoringOnly': True, 'shippingRepresentation': cfg['shippingRepresentation'],
        'blenderVersion': bpy.app.version_string, 'config': cfg,
        'cameraWorldMatrix': camera_matrix, 'cameraShift': [camera.data.shift_x, camera.data.shift_y],
        'cameraNeverMovesBetweenDirections': True,
        'rigBones': {bone.name: {'parent': bone.parent.name if bone.parent else None,
                                'head': rounded(bone.head_local), 'tail': rounded(bone.tail_local),
                                'length': round(bone.length, 6)} for bone in rig.data.bones},
        'sourceHashes': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                         for name in ['tools/build-character-factory.py', 'tools/swordsman-walk-cycle.py',
                                      'authoring/characters/swordsman-production/factory/canonical/definition.json']},
        'frames': records})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--save-scene', type=Path)
    parser.add_argument('--scene', type=Path, help='Render saved editable canonical source without rebuilding')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    cfg = json.loads(args.config.read_text(encoding='utf-8'))
    if args.scene:
        bpy.ops.wm.open_mainfile(filepath=str(args.scene.resolve()))
        scene = bpy.context.scene
        if json.loads(scene['factory_config']) != cfg:
            raise ValueError('Saved scene/config drift; update explicit source contract before rendering')
    else:
        scene = build(cfg)
    render(cfg, scene, args.output.resolve())
    if args.save_scene:
        args.save_scene.parent.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = '//guides/Neutral/S/Composite/frame_000.png'
        bpy.ops.wm.save_as_mainfile(filepath=str(args.save_scene.resolve()), compress=True)
    print('PASS: authoring source and eight real neutral directions; owner approval pending', flush=True)


if __name__ == '__main__':
    main()
