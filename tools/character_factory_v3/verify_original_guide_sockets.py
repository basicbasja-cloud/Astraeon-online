"""Verify saved guide sockets against actual posed wrist/knuckle geometry."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


def main():
    import bpy
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():
        raise ValueError('Preserve previous socket verification')
    manifest = json.loads((args.library/'manifest.json').read_text())
    results = []
    for suffix in ['blend', 'glb']:
        path = args.library/('original-guide-actions.'+suffix)
        if suffix == 'blend':
            bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
        else:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
        rig = next(obj for obj in bpy.data.objects if obj.type == 'ARMATURE')
        scene = bpy.context.scene
        for name in manifest['sockets']:
            if not bpy.data.objects.get(name):
                raise ValueError('Missing saved socket '+name)
        errors = {name: 0. for name in manifest['sockets']}
        samples = 0
        for row in manifest['actions']:
            actions = [a for a in bpy.data.actions if a.name == row['action_name'] or a.name.startswith(row['action_name']+'_')]
            if len(actions) != 1:
                raise ValueError('Missing or ambiguous saved action')
            action = actions[0]
            rig.animation_data_create()
            rig.animation_data.action = action
            rig.animation_data.action_slot = action.slots[0]
            first, last = action.frame_range
            for index in range(row['frames']):
                frame = first+(last-first)*index/max(1, row['frames']-1)
                scene.frame_set(math.floor(frame), subframe=frame % 1)
                bpy.context.view_layer.update()
                for name, spec in manifest['sockets'].items():
                    if 'WeaponGrip' in name:
                        side = name[-1].lower()
                        expected = rig.matrix_world@((rig.pose.bones['index_01_'+side].head+rig.pose.bones['pinky_01_'+side].head)*.5)
                    else:
                        expected = rig.matrix_world@rig.pose.bones[spec['bone']].head
                    error = (bpy.data.objects[name].matrix_world.translation-expected).length
                    errors[name] = max(errors[name], error)
                samples += 1
        if max(errors.values()) > 1e-4:
            raise ValueError('Saved socket does not match the actual posed pivot: '+str(errors))
        results.append({'format': suffix, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'sampled_poses': samples, 'maximum_socket_error_m': errors})
        print('ORIGINAL_GUIDE_SOCKETS_PASS', suffix, samples, max(errors.values()), flush=True)
    receipt = {'status': 'SAVED_WRIST_AND_KNUCKLE_SOCKETS_MATCH_ACTUAL_POSES',
               'formats': results, 'socket_count': len(manifest['sockets']),
               'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'painted_hand_or_weapon_fit_approved': False,
               'note': 'Weapon profile still needs a local orientation/offset; wrist and knuckle pivots are distinct.'}
    args.output.write_text(json.dumps(receipt, indent=2)+'\n')


if __name__ == '__main__':
    main()
