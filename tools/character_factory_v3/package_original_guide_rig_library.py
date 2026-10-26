"""Package the original tall human guide skeleton and actual sampled poses.

No F01 mesh/retarget is used. Existing guide metadata, art and source GLB stay
read-only. Uniform sample-index clips are an editable authoring library, not
production event/timing or visual approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    import bpy
    from mathutils import Matrix
    from bpy_extras.anim_utils import action_get_channelbag_for_slot
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root = args.repository_root.resolve()
    base = root/'authoring/characters/factory-v3/patch-0.0.1'
    replay = base/'research/native-rig-library-20261026'
    progress_path = replay/'progress.json'
    progress = json.loads(progress_path.read_text())
    ledger_path = base/'ledger.json'
    ledger = json.loads(ledger_path.read_text())
    source = root/'authoring/characters/factory-v3/motions/raw/mesh2motion/human-base-animations.glb'
    if args.output.exists():
        raise ValueError('Use a fresh output; preserve existing rig packages')
    if progress['successful_jobs'] != 48 or progress['failed_jobs']:
        raise ValueError('Complete verified source metadata is required')
    if sha(source) != '406eb0a8dc4ab366e623b79b6e3005a4951392e1bda78ae39c1099d31147733c':
        raise ValueError('Original Mesh2Motion source changed')
    pins = {str(p): sha(p) for p in [source, progress_path, ledger_path]}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    rig.animation_data_clear()
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH' and obj.name != 'Mannequin':
            bpy.data.objects.remove(obj, do_unlink=True)
    if not bpy.data.objects.get('Mannequin'):
        raise ValueError('Missing original tall source guide mesh')
    scene = bpy.context.scene
    scene.render.fps = 25
    scene.render.fps_base = 2
    scene.render.resolution_x = scene.render.resolution_y = 1536
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.render_aa = '8'
    ordered = sorted(rig.pose.bones, key=lambda b: len(b.parent_recursive))
    rows = []
    args.output.mkdir(parents=True)
    for job in progress['jobs']:
        path = replay/'source'/(job['job']+'.json')
        if sha(path) != job['source_export_sha256']:
            raise ValueError('Source skeleton replay changed')
        data = json.loads(path.read_text())
        guide = base/'guides'/job['job']/'manifest.json'
        if sha(guide) != data['source_manifest_sha256']:
            raise ValueError('Replay does not match the actual source guide')
        pins[str(path)] = sha(path)
        pins[str(guide)] = sha(guide)
        if set(data['rest_bones']) != set(rig.pose.bones.keys()):
            raise ValueError('Source skeleton bone set differs')
        frames = data['frames']
        action = bpy.data.actions.new('Guide_'+job['uses'][0].replace('/', '_')+'__'+job['job'])
        action.use_fake_user = True
        action.use_frame_range = True
        action.frame_start = 1
        action.frame_end = len(frames)
        action['guide_job'] = job['job']
        action['motion_provider'] = job['motion_provider']
        action['timing_status'] = 'SAMPLE_INDEX_NOT_PRODUCTION_TIMING'
        rig.animation_data_create()
        rig.animation_data.action = action
        previous = {}
        for row in frames:
            scene.frame_set(row['index']+1)
            for bone in ordered:
                bone.rotation_mode = 'QUATERNION'
                bone.matrix_basis = Matrix.Identity(4)
            bpy.context.view_layer.update()
            inverse = rig.matrix_world.inverted()
            for bone in ordered:
                bone.matrix = inverse@Matrix(row['bones'][bone.name]['world_matrix'])
                bpy.context.view_layer.update()
            for bone in ordered:
                location, rotation, scale = bone.matrix_basis.decompose()
                if bone.name in previous and previous[bone.name].dot(rotation) < 0:
                    rotation.negate()
                previous[bone.name] = rotation.copy()
                bone.location, bone.rotation_quaternion, bone.scale = location, rotation, scale
                for prop in ['location', 'rotation_quaternion', 'scale']:
                    bone.keyframe_insert(data_path=prop, frame=row['index']+1, group=bone.name)
        bag = action_get_channelbag_for_slot(action, rig.animation_data.action_slot)
        for curve in bag.fcurves:
            for key in curve.keyframe_points:
                key.interpolation = 'LINEAR'
        rows.append({'job': job['job'], 'action_name': action.name, 'uses': job['uses'],
                     'frames': len(frames), 'motion_provider': job['motion_provider'],
                     'source_replay_sha256': sha(path),
                     'guide_sha256': sha(guide), 'source_samples': [
                         {'action': f['action'], 'frame': f['source_frame']} for f in frames]})
        print('ORIGINAL_GUIDE_ACTION', len(rows), job['job'], flush=True)
    walk = next(r for r in rows if 'Mage/Walk' in r['uses'])
    views = json.loads((base/'guides'/walk['job']/'manifest.json').read_text())['views']
    for direction, view in views.items():
        spec = view['camera']
        camera = bpy.data.objects.new('CAM_'+direction, bpy.data.cameras.new('CAM_'+direction))
        scene.collection.objects.link(camera)
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = spec['ortho_scale']
        camera.location = spec['location']
        camera.rotation_euler = spec['rotation']
    for name, bone_name in {'Head': 'head', 'Hand_R': 'hand_r', 'Hand_L': 'hand_l',
                            'Back': 'spine_03', 'Waist': 'pelvis',
                            'Foot_R': 'foot_r', 'Foot_L': 'foot_l'}.items():
        socket = bpy.data.objects.new('SOCKET_'+name, None)
        scene.collection.objects.link(socket)
        socket.parent = rig
        socket.parent_type = 'BONE'
        socket.parent_bone = bone_name
        # Bone-parent coordinates are based at the tail; offset to the head.
        socket.location = (0, -rig.data.bones[bone_name].length, 0)
        socket.empty_display_size = .035
    rig.animation_data.action = bpy.data.actions[walk['action_name']]
    rig.animation_data.action_slot = rig.animation_data.action.slots[0]
    scene.camera = bpy.data.objects['CAM_SE']
    scene.frame_start, scene.frame_end = 1, walk['frames']
    scene.frame_set(1)
    bpy.context.view_layer.update()
    for side, label in [('l', 'L'), ('r', 'R')]:
        hand = rig.pose.bones['hand_'+side]
        local_index = hand.matrix.inverted()@rig.pose.bones['index_01_'+side].head
        local_pinky = hand.matrix.inverted()@rig.pose.bones['pinky_01_'+side].head
        pivot = (local_index+local_pinky)*.5
        socket = bpy.data.objects.new('SOCKET_WeaponGrip_'+label, None)
        scene.collection.objects.link(socket)
        socket.parent = rig
        socket.parent_type = 'BONE'
        socket.parent_bone = hand.name
        socket.location = pivot
        socket.location.y -= hand.bone.length
        socket.empty_display_size = .025
        socket['pivot_definition'] = 'midpoint of index_01 and pinky_01 bone heads; wrist-local, not wrist origin'
    scene['package_status'] = 'ORIGINAL_TALL_GUIDE_MESH_NOT_FINISHED_CHARACTER_ART'
    bpy.context.preferences.filepaths.save_version = 0
    blend = args.output/'original-guide-actions.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()), compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend.resolve()))
    rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    scene = bpy.context.scene
    for record in rows:
        action = bpy.data.actions[record['action_name']]
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        data = json.loads((replay/'source'/(record['job']+'.json')).read_text())
        errors = []
        for row in data['frames']:
            scene.frame_set(row['index']+1)
            bpy.context.view_layer.update()
            errors.append(max(abs((rig.matrix_world@rig.pose.bones[name].matrix)[r][c]-target['world_matrix'][r][c])
                              for name, target in row['bones'].items() for r in range(4) for c in range(4)))
        record['maximum_reopened_matrix_error'] = max(errors)
        if max(errors) > 3e-5:
            raise ValueError('Saved original guide action differs: '+record['job'])
        print('ORIGINAL_GUIDE_REOPEN', record['job'], max(errors), flush=True)
    if any(sha(p) != digest for p, digest in pins.items()):
        raise ValueError('A source input changed during packaging')
    result = {'status': 'EDITABLE_ORIGINAL_GUIDE_RIG_NOT_COMPLETE_CHARACTERS',
              'actions': rows, 'action_count': len(rows), 'bone_count': len(rig.data.bones),
              'sample_count': sum(r['frames'] for r in rows), 'cameras': list(views),
              'camera_note': 'Mage/Walk canonical cameras; action-specific source cameras remain in pinned guide manifests.',
              'source_sha256': pins, 'outputs': {blend.name: sha(blend)},
              'implementation_sha256': sha(__file__), 'F01_target_used': False,
              'mesh_note': 'Unchanged original Mesh2Motion mannequin; no finished class/sex meshes claimed.',
              'production_timing_authored': False, 'new_complete_characters': 0,
              'maximum_reopened_matrix_error': max(r['maximum_reopened_matrix_error'] for r in rows)}
    result['sockets'] = {obj.name: {'bone': obj.parent_bone, 'pivot_definition': obj.get('pivot_definition', 'bone head / wrist reference')}
                         for obj in scene.objects if obj.name.startswith('SOCKET_')}
    (args.output/'manifest.json').write_text(json.dumps(result, indent=2)+'\n')
    (args.output/'packager-source.py').write_bytes(Path(__file__).read_bytes())
    print('ORIGINAL_GUIDE_LIBRARY_PASS', result['sample_count'], flush=True)


if __name__ == '__main__':
    main()
